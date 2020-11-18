from . import BaseConfig
from .model import ModelBuilder
from pydantic import create_model
from .training import TrainingBuilder
from . import BaseBuilder



class ExperimentBuilder(BaseBuilder):
    def build_config(self, cfg):
        model = ModelBuilder().build_config(cfg['model'])
        training = TrainingBuilder().build_config(cfg['training'])
        config = create_model(
            'ExperimentModel',
            training=(training, ...),
            model=(model, ...),
            __base__=BaseConfig
        )
        return config

    def parse(self, cfg):
        config_cls = self.build_config(cfg)
        return config_cls(**cfg)
