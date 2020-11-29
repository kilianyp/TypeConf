from typeconf.libs.torch.optim import OptimizerConfig, AdadeltaConfig, AdagradConfig
# This takes quite some time to import
from torch.optim import Adadelta, Adagrad
from torch.nn import ParameterList, Parameter
import torch
import pytest


@pytest.fixture
def params():
    return ParameterList([Parameter(torch.Tensor(1))])

def test_adadelta(params):
    cfg = {
        "name": "Adadelta"
    }
    config = OptimizerConfig(**cfg)
    assert isinstance(config, AdadeltaConfig)
    optimizer = config.build(params)
    assert isinstance(optimizer, Adadelta)

def test_adagrad(params):
    cfg = {
        "name": "Adagrad"
    }
    config = OptimizerConfig(**cfg)
    assert isinstance(config, AdagradConfig)
    optimizer = config.build(params)
    assert isinstance(optimizer, Adagrad)
