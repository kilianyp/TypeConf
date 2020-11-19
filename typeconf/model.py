from . import BaseConfig
from . import SelectBuilder
from pydantic import FilePath


class ModelConfig(BaseConfig):
    name : str
    weights : FilePath

    def build(self, *args, **kwargs):
        model = self._build(*args, **kwargs)
        # torch.load(cfg.weights)
        return model


class ModelBuilder(SelectBuilder):
    pass


class UnetModel(object):
    def __init__(self, num_classes):
        self.num_classes = num_classes


class UnetModelConfig(ModelConfig):
    num_classes : int

    def build(self):
        return UnetModel(self.num_classes)


@ModelBuilder.register('Unet')
class UnetModelBuilder(ModelBuilder):
    def build_config(self, cfg):
        return UnetModelConfig


class DummyModelConfig(ModelConfig):
    test : str


@ModelBuilder.register('dummy')
class DummyModelBuilder(ModelBuilder):
    def build_config(self, cfg):
        return DummyModelConfig
    def build(self, cfg):
        return cfg.test


