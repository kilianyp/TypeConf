import pytest
from typeconf.experiment import ExperimentConfig
from pydantic import ValidationError
from typeconf.model import UnetModelConfig, ModelConfig, DummyModelConfig, UnetModel


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


def test_training(cfg):
    experiment_cfg = ExperimentConfig.parse(cfg)
    assert experiment_cfg.training.max_steps == 30


def test_unet_builder(unet_cfg):
    model_cfg = ModelConfig.parse(unet_cfg)
    assert isinstance(model_cfg, UnetModelConfig)
    assert model_cfg.num_classes == 1
    model = model_cfg.build()
    assert isinstance(model, UnetModel)

def test_dummy_builder(dummy_cfg):
    model_cfg = ModelConfig.parse(dummy_cfg)
    assert isinstance(model_cfg, DummyModelConfig)

def test_missing_attribute():
    cfg = {"name": "dummy"}
    with pytest.raises(ValidationError):
        model_cfg = ModelConfig.parse(cfg)

def test_missing_name():
    cfg = {"weights": "dummy"}
    with pytest.raises(ValueError):
        model_cfg = ModelConfig.parse(cfg)

def test_missing_weights():
    cfg = {"name": "Unet", "weights": "dummy", "num_classes": 1}
    with pytest.raises(ValidationError):
        model_cfg = ModelConfig.parse(cfg)
