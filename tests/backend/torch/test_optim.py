from typeconf.backend.torch.optim import OptimizerConfig
from typeconf.backend.torch.optim.adadelta import AdadeltaConfig


def test_adadelta():
    cfg = {
        "name": "Adadelta"
    }
    config = OptimizerConfig.parse(cfg)
    assert isinstance(config, AdadeltaConfig)

