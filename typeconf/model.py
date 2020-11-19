from . import SelectConfig
from pydantic import FilePath
from typing import Optional


class ModelConfig(SelectConfig):
    weights : Optional[FilePath]

    def build(self, *args, **kwargs):
        model = self._build(*args, **kwargs)
        # torch.load(cfg.weights)
        return model


class UnetModel(object):
    def __init__(self, num_classes):
        self.num_classes = num_classes


@ModelConfig.register('Unet')
class UnetModelConfig(ModelConfig):
    num_classes : int

    def _build(self):
        return UnetModel(self.num_classes)

    @classmethod
    def build_config(cls, cfg):
        return cls


@ModelConfig.register('dummy')
class DummyModelConfig(ModelConfig):
    test : str

    @classmethod
    def build_config(cls, cfg):
        return cls
