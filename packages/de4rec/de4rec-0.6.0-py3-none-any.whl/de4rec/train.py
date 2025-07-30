from dataclasses import dataclass, field
from typing import Optional

import evaluate
import numpy as np
import torch
from tqdm import tqdm
from transformers import PretrainedConfig, PreTrainedModel, Trainer, TrainingArguments
from transformers.modeling_outputs import ModelOutput
from transformers.trainer_utils import EvalPrediction


class ListDataset(torch.utils.data.Dataset):
    """
    List of tuples of uder_id, item_id, label
    """

    def __init__(self, data: list[list[int, int, int]]):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

    def __getitems__(self, idx_list):
        return [self.data[_] for _ in idx_list]

    def distinct_size(self) -> int:
        res = set()
        for lst in self.data:
            res.update(lst)
        return len(res)


class DataCollatorForList:
    """
    Convert DataList to named tensors and move to device
    """

    def __call__(self, batch):
        tbatch = torch.tensor(batch)
        return {
            "user_ids": tbatch[:, 0:1],
            "item_ids": tbatch[:, 1:2],
            "labels": tbatch[:, 2],
        }


@dataclass
class DualEncoderOutput(ModelOutput):
    """
    Output of the DualEncoder model
    """

    loss: Optional[torch.FloatTensor] = None
    logits: Optional[torch.FloatTensor] = None
    labels: Optional[torch.LongTensor] = None


@dataclass
class DualEncoderSplit:
    train_dataset: ListDataset
    eval_dataset: ListDataset
    test_dataset: ListDataset = field(init=False)


class DualEncoderConfig(PretrainedConfig):
    model_type = "DualEncoder"

    def __init__(
        self,
        users_size: int = None,
        items_size: int = None,
        embedding_dim: int = None,
        margin: float = 0.85,
        max_norm: float = 5.0,
        **kwargs,
    ):
        self.users_size = users_size
        self.items_size = items_size
        self.embedding_dim = embedding_dim
        self.margin = margin
        self.max_norm = max_norm
        super().__init__(**kwargs)


class DualEncoderModel(PreTrainedModel):
    config_class = DualEncoderConfig

    def __init__(self, config: DualEncoderConfig):
        super().__init__(config)
        self.user_embeddings = torch.nn.Embedding(
            config.users_size, config.embedding_dim, max_norm=config.max_norm
        )
        self.item_embeddings = torch.nn.Embedding(
            config.items_size, config.embedding_dim, max_norm=config.max_norm
        )
        self.cel = torch.nn.CosineEmbeddingLoss(margin=config.margin, reduction="mean")
        self.cs = torch.nn.CosineSimilarity()

    def forward(self, **kwargs) -> DualEncoderOutput:
        user_embs = self.user_embeddings(kwargs["user_ids"]).squeeze(1)
        item_embs = self.item_embeddings(kwargs["item_ids"]).squeeze(1)
        logits = self.cs(user_embs, item_embs)
        loss = self.cel(user_embs, item_embs, kwargs["labels"])
        return DualEncoderOutput(loss=loss, logits=logits, labels=kwargs["labels"])

    def recommend_topk_by_user_ids(
        self, user_ids: list[int], top_k: int
    ) -> list[list[int]]:
        """
        Recommend by known user_id. It have to be in the model.
        You may give a list of known user_ids
        ---
        Return:
        A list of list of item ids
        """
        recommended_item_ids = []
        for user_id in user_ids:
            recommended_item_ids.append(
                torch.topk(
                    self.cs(
                        self.user_embeddings.weight[user_id, :],
                        self.item_embeddings.weight,
                    ).detach(),
                    k=top_k,
                ).indices.tolist()
            )
        return recommended_item_ids

    def recommend_topk_by_item_ids(self, item_ids: list[int], top_k: int) -> list[int]:
        """
        In case of a new user (which has no embedding) may take a list of item_ids of the new user, average them, and use as an surrogate new user embedding.
        ---
        Return:
        A list of item_ids
        """
        return torch.topk(
            self.cs(
                self.item_embeddings.weight[item_ids, :].mean(dim=0),
                self.item_embeddings.weight,
            ).detach(),
            k=top_k,
        ).indices.tolist()


class DualEncoderRecommender:
    def __init__(self, model: DualEncoderModel):
        model.eval()
        with torch.no_grad():
            self.user_normed_embs = (
                model.user_embeddings.weight
                / torch.functional.norm(model.user_embeddings.weight, dim=1).unsqueeze(
                    -1
                )
            )
            self.item_normed_embs = (
                model.item_embeddings.weight
                / torch.functional.norm(model.item_embeddings.weight, dim=1).unsqueeze(
                    -1
                )
            )

    def batch_recommend_topk_by_user_ids(
        self, user_ids: list[int], top_k: int, batch_size: int
    ) -> list[list[int]]:
        recommended_item_ids = []
        user_ids_size = len(user_ids)
        for batch in tqdm(range(0, user_ids_size, batch_size)):
            recommended_item_ids += (
                torch.matmul(
                    self.user_normed_embs[user_ids[batch : batch + batch_size]],
                    self.item_normed_embs.T,
                )
                .topk(top_k, dim=1)
                .indices.detach()
                .tolist()
            )

        return recommended_item_ids

    def batch_recommend_topk_by_item_ids(
        self, item_ids_list: list[list[int]], top_k: int, batch_size: int
    ) -> list[list[int]]:
        recommended_item_ids = []
        item_ids_list_size = len(item_ids_list)
        for batch in tqdm(range(0, item_ids_list_size, batch_size)):
            batch_item_id_meaned = []
            for item_ids in item_ids_list[batch : batch + batch_size]:
                batch_item_id_meaned.append(self.item_normed_embs[item_ids].mean(dim=0))

            recommended_item_ids += (
                torch.matmul(
                    torch.stack(batch_item_id_meaned),
                    self.item_normed_embs.T,
                )
                .topk(top_k, dim=1)
                .indices.detach()
                .tolist()
            )

        return recommended_item_ids


class DualEncoderTrainingArguments(TrainingArguments):
    def __init__(self, **kwargs):
        self._kwargs = kwargs
        super().__init__(
            output_dir=kwargs.get("output_dir", "./results"),
            eval_strategy=kwargs.get("eval_strategy", "steps"),
            logging_steps=kwargs.get("logging_steps", 10000),
            prediction_loss_only=False,
            save_strategy="best",
            load_best_model_at_end=True,
            metric_for_best_model=kwargs.get("metric_for_best_model", "eval_loss"),
            learning_rate=kwargs.get("learning_rate", 2e-3),
            per_device_train_batch_size=kwargs.get(
                "per_device_train_batch_size", 4 * 256
            ),
            per_device_eval_batch_size=kwargs.get(
                "per_device_eval_batch_size", 4 * 256
            ),
            num_train_epochs=kwargs.get("num_train_epochs", 3),
            weight_decay=0.01,
            use_cpu=kwargs.get("use_cpu", True),
            data_seed=42,
            seed=42,
            disable_tqdm=False,
            full_determinism=True,
            save_total_limit=11,
            save_safetensors=True,
            do_train=True,
            do_eval=True,
            label_names=[
                "labels",
            ],
        )


class DualEncoderTrainer(Trainer):
    roc_auc_score = evaluate.load("roc_auc")

    def __init__(
        self,
        model: DualEncoderModel,
        training_arguments: DualEncoderTrainingArguments,
        dataset_split: DualEncoderSplit,
        **kwargs,
    ):

        super().__init__(
            model=model,
            args=training_arguments,
            data_collator=DataCollatorForList(),
            train_dataset=dataset_split.train_dataset,
            eval_dataset=dataset_split.eval_dataset,
            compute_metrics=DualEncoderTrainer.compute_metrics,
        )
        self._save_path = kwargs.get("save_path", "./saved")
        self._kwargs = kwargs

    def save_all_metrics(self, eval_dataset: ListDataset):
        metrics = self.predict(test_dataset=eval_dataset)
        self.save_metrics(split="all", metrics=metrics)

    @staticmethod
    def compute_metrics(eval_pred: EvalPrediction):
        (logits, labels), _ = eval_pred
        prediction_scores = logits * 2 - 1
        return DualEncoderTrainer.roc_auc_score.compute(
            prediction_scores=prediction_scores, references=labels
        )


@dataclass
class DualEncoderDatasets:
    """
    Take interactions list : (user_id, item_id) and two dimensions: users_size and items_size.
    Do negative sampling.
    Do train-eval split.

    """

    interactions: list[tuple[int, int]]
    users_size: int
    items_size: int

    @staticmethod
    def neg_choice(
        freq_dist: np.array,
        pos_item_ids: list[int],
        neg_per_sample: int,
        item_id_to_choice: np.array,
    ) -> list[int]:
        """
        Choose neg_per_sample times the number of pos_item_ids based on the truncated marginal frequency distribution.
        --
        Return:
        list of item_ids
        """
        n_samples = neg_per_sample * len(set(pos_item_ids))

        try:
            return np.random.choice(
                item_id_to_choice, size=n_samples, replace=False, p=freq_dist
            ).tolist()
        except ValueError:
            print(item_id_to_choice.shape, n_samples)
            return [0] * n_samples

    def make_pos_distributions(
        self, interactions: list[tuple[int, int]]
    ) -> tuple[np.array, dict]:
        freq_dist = np.ones(self.items_size)
        pos_interactions = {}
        for user_id, item_id in interactions:
            freq_dist[item_id] = freq_dist[item_id] + 1
            pos_interactions[user_id] = pos_interactions.get(user_id, []) + [
                item_id,
            ]

        return freq_dist, pos_interactions

    def make_negative_samples(
        self, freq_margin: float, neg_per_sample: int
    ) -> list[list[int]]:
        freq_dist, pos_interactions = self.make_pos_distributions(self.interactions)
        freq_dist = np.log10(freq_dist)
        freq_margin_num = int(len(freq_dist) * freq_margin)
        item_id_to_choice = np.argsort(freq_dist)[-freq_margin_num:]
        freq_dist = freq_dist[item_id_to_choice]
        freq_dist = freq_dist / freq_dist.sum()

        pos_neg_interactions = list(
            map(
                lambda tup: (
                    tup[0],
                    tup[1],
                    self.neg_choice(
                        freq_dist=freq_dist,
                        pos_item_ids=tup[1],
                        neg_per_sample=neg_per_sample,
                        item_id_to_choice=item_id_to_choice,
                    ),
                ),
                pos_interactions.items(),
            )
        )
        return pos_neg_interactions

    def create_dataset(
        self, pos_neg_interactions: list[list[int, int]]
    ) -> list[list[int, int, int]]:
        dataset = []
        for user_id, pos_item_ids, neg_item_ids in tqdm(pos_neg_interactions):
            dataset += list(
                map(lambda item_id: (user_id, item_id, 1), pos_item_ids)
            ) + list(map(lambda item_id: (user_id, item_id, -1), neg_item_ids))
        return dataset

    def __train_eval_split(self, dataset: ListDataset) -> DualEncoderSplit:
        generator = torch.Generator().manual_seed(42)
        train_dataset, eval_dataset = torch.utils.data.random_split(
            dataset, [0.95, 0.05], generator=generator
        )
        return DualEncoderSplit(train_dataset, eval_dataset)

    def save(self, save_path: str = "./saved"):
        pass

    def split(
        self, freq_margin: float = 0.15, neg_per_sample: int = 3
    ) -> DualEncoderSplit:
        """
        Make negative sampling and split dataset
        ---
        Return:
        train_dataset, eval_dataset
        """
        pos_neg_interactions = self.make_negative_samples(
            freq_margin=freq_margin, neg_per_sample=neg_per_sample
        )
        dataset = ListDataset(self.create_dataset(pos_neg_interactions))
        return self.__train_eval_split(dataset)


class DualEncoderLoadData(DualEncoderDatasets):
    def __init__(self, **kwargs):

        _interactions_path = kwargs.get(
            "interactions_path", "dataset/ml-1m/ratings.dat"
        )
        assert _interactions_path
        _interactions = self.load_list_of_int_int_from_path(_interactions_path)

        _users_size = max([tu[0] for tu in _interactions]) + 1
        _items_size = max([tu[1] for tu in _interactions]) + 1

        super().__init__(
            interactions=_interactions, users_size=_users_size, items_size=_items_size
        )

    def load_list_of_int_int_from_path(
        self, path: str, sep: str = "::"
    ) -> list[tuple[int, int]]:
        with open(path, "r", encoding="utf-8") as fn:
            res = list(
                map(
                    lambda row: (int(row[0]), int(row[1])),
                    map(
                        lambda row: row.strip().split(sep)[:2],
                        fn.read().strip().split("\n"),
                    ),
                )
            )
        return res


if __name__ == "__main__":

    pass
