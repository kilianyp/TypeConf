import json
import os
from typeconf.irconfig import IRConfig
from typeconf import BaseConfig


def test_preset(tmp_path):
    # create a simple preset there

    preset = {
        "testa": 1,
        "testb": 2
    }

    with open(os.path.join(tmp_path, 'test.json'), 'w') as f:
        json.dump(preset, f)

    IRConfig.register_preset_dir(tmp_path)
    cfg = {
        "preset": "${preset:test.json}"
    }
    cfg = IRConfig.create(cfg)
    cfg = IRConfig.to_container(cfg, resolve=True)
    assert cfg['preset'] == preset


class NestedConfig(BaseConfig):
    test : int = 1


class Config(BaseConfig):
    nested : NestedConfig


def test_integration(tmp_path):
    preset = {
        "test": 2,
    }

    with open(os.path.join(tmp_path, 'test2.json'), 'w') as f:
        json.dump(preset, f)

    IRConfig.register_preset_dir(tmp_path)
    cfg = {"nested": "${preset:test2.json}"}
    cfg = Config(**cfg)
    assert cfg.nested.test == 2
