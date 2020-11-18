from . import BaseConfig
from . import BaseBuilder


class TrainingConfig(BaseConfig):
    max_steps : int = 300
    # optimizer : OptimizerConfig


class TrainingBuilder(BaseBuilder):
    def build_config(self, config):
        return TrainingConfig


