from . import BaseConfig
from . import SelectBuilder
from pydantic import FilePath


class Model(BaseConfig):
    name : str
    weights : FilePath


class ModelBuilder(SelectBuilder):
    def build(self, cfg):
        model = self._build(cfg)
        torch.load(cfg.weights)



class UnetModel(Model):
    num_classes : int


@ModelBuilder.register('Unet')
class UnetModelBuilder(ModelBuilder):
    def build_config(self, cfg):
        return UnetModel


class DummyModel(Model):
    test : str


@ModelBuilder.register('dummy')
class DummyModelBuilder(ModelBuilder):
    def build_config(self, cfg):
        return DummyModel
    def build(self, cfg):
        return cfg.test


