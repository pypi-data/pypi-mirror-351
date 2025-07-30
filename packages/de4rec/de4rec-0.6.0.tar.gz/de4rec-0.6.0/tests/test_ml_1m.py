import sys

sys.path.append("src")

import numpy as np
import pytest

from de4rec import (
    DualEncoderLoadData,
    DualEncoderConfig,
    DualEncoderModel,
    DualEncoderTrainer,
    DualEncoderTrainingArguments,
    DualEncoderRecommender
)
import torch

class TestML1M:
    @pytest.fixture
    def save_path(self,):
        return "./ml_1m/"


    @pytest.fixture
    def datasets(self,):
        datasets = DualEncoderLoadData(
            interactions_path="dataset/ml-1m/ratings.dat",
            users_path="dataset/ml-1m/users.dat",
            items_path="dataset/ml-1m/movies.dat",
        )
        return datasets


    def test_datasets(self, datasets):
        assert datasets.items_size == 3953
        assert datasets.users_size == 6041


    def test_neg_choice(self, datasets):
        neg_item_ids = datasets.neg_choice(
            freq_dist=np.array([1, 2, 3]),
            pos_item_ids=[
                1,
            ],
            freq_margin=1,
            neg_per_sample=1,
        )
        assert len(neg_item_ids) == 1
        assert neg_item_ids[0] in [0, 2]


    def test_make_pos_distributions(self, datasets):
        freq_dist, pos_interactions = datasets.make_pos_distributions(datasets.interactions)
        assert freq_dist.sum() > 3953
        assert len(pos_interactions) >= 6040


    @pytest.fixture
    def dataset_split(self, datasets):
        return datasets.split(freq_margin=1.0, neg_per_sample=1)


    def test_run(self, dataset_split):
        assert len(dataset_split.train_dataset) > 1
        assert len(dataset_split.eval_dataset) > 1


    def test_config(self, save_path):
        config = DualEncoderConfig(users_size=101, items_size=102, embedding_dim=32)
        config.save_pretrained(save_path)


    def test_trainer(self, datasets, dataset_split, save_path):
        config = DualEncoderConfig(
            users_size=datasets.users_size,
            items_size=datasets.items_size,
            embedding_dim=32,
        )
        model = DualEncoderModel(config)

        training_arguments = DualEncoderTrainingArguments(
            logging_steps=1000,
            learning_rate=1e-3,
            use_cpu=not torch.cuda.is_available(),
            per_device_train_batch_size=4 * 256,
        )

        trainer = DualEncoderTrainer(
            model=model, training_arguments=training_arguments, dataset_split=dataset_split
        )
        trainer.train()
        trainer.save_model(save_path)
        assert trainer

    @pytest.fixture
    def model(self, save_path) -> DualEncoderModel: 
        return DualEncoderModel.from_pretrained(save_path)

    def test_recomm(self, model : DualEncoderModel, datasets):
        assert sum(p.numel() for p in model.parameters() if p.requires_grad) > 1000
        sample = 30
        recommender = DualEncoderRecommender(model=model)
        rec_items = recommender.batch_recommend_topk_by_user_ids(user_ids = list(range(sample)), top_k =  3, batch_size = 10)
        assert len(rec_items) == sample
