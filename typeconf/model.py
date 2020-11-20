from . import SelectConfig
from pydantic import FilePath
from typing import Optional
from abc import abstractmethod


class ModelConfig(SelectConfig):
    weights : Optional[FilePath]

    def build(self, *args, **kwargs):
        model = self._build(*args, **kwargs)
        # torch.load(cfg.weights)
        return model

    @abstractmethod
    def _build(self, *args, **kwargs):
        pass


class UnetModel(object):
    def __init__(self, num_classes):
        self.num_classes = num_classes


@ModelConfig.register('Unet')
class UnetModelConfig(ModelConfig):
    num_classes : int

    def _build(self):
        return UnetModel(self.num_classes)

@ModelConfig.register('dummy')
class DummyModelConfig(ModelConfig):
    test : str

    def _build(self):
        return None
