from . import BaseConfig
from .model import ModelConfig
from pydantic import create_model
from .training import TrainingConfig
from typing import Optional



class ExperimentConfig(BaseConfig):
    seed : Optional[int]
    model : ModelConfig
    training : TrainingConfig

    @classmethod
    def build_config(cls, cfg):
        model = ModelConfig.build_config(cfg['model'])
        training = TrainingConfig.build_config(cfg['training'])

        config = create_model(
            'ExperimentModel',
            training=(training, ...),
            model=(model, ...),
            __base__=cls
        )
        return config
