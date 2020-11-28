from typeconf.model import UnetModelConfig, ModelConfig, DummyModelConfig, UnetModel
from typeconf import BaseConfig
from typing import Tuple
from pydantic import ValidationError
import pytest


def test_multi_select():
    class MultiModel(BaseConfig):
        models : Tuple[UnetModelConfig, DummyModelConfig]
        # models : List[ModelConfig]

    cfg = {
        "models": [
            {
                "name": "Unet",
                "num_classes": 0
            },
            {
                "name": "dummy",
                "test": 1
            }
        ]
    }
    config = MultiModel.parse(**cfg)
    assert isinstance(config.models[0], UnetModelConfig)
    assert isinstance(config.models[1], DummyModelConfig)



@pytest.fixture
def unet_cfg():
    cfg = {
        "name": "Unet",
        "num_classes": 1,
        "weights": "tests/mock_weights.pt",
    }
    return cfg


@pytest.fixture
def dummy_cfg():
    cfg = {
        "name": "dummy",
        "weights": "tests/mock_weights.pt",
        "test": 1
    }
    return cfg


@pytest.fixture
def cfg(unet_cfg):
    cfg = {
        "model": unet_cfg,
        "training": {
            "optimizer": {
                "name": "adagrad"
            },
            "max_steps": 30,
        },
    }
    return cfg


def test_unet_builder(unet_cfg):
    model_cfg = ModelConfig.parse(**unet_cfg)
    assert isinstance(model_cfg, UnetModelConfig)
    assert model_cfg.num_classes == 1
    model = model_cfg.build()
    assert isinstance(model, UnetModel)

def test_dummy_builder(dummy_cfg):
    model_cfg = ModelConfig.parse(**dummy_cfg)
    assert isinstance(model_cfg, DummyModelConfig)

def test_missing_attribute():
    cfg = {"name": "dummy"}
    with pytest.raises(ValidationError):
        model_cfg = ModelConfig.parse(**cfg)

def test_missing_name():
    cfg = {"weights": "dummy"}
    with pytest.raises(ValueError):
        model_cfg = ModelConfig.parse(**cfg)

def test_missing_weights():
    cfg = {"name": "Unet", "weights": "dummy", "num_classes": 1}
    with pytest.raises(ValidationError):
        model_cfg = ModelConfig.parse(**cfg)
