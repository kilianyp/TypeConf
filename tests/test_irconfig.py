import json
import os
from typeconf.irconfig import IRConfig
from typeconf import BaseConfig
import pytest


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


def test_preset_integration(tmp_path):
    preset = {
        "test": 2,
    }

    with open(os.path.join(tmp_path, 'test2.json'), 'w') as f:
        json.dump(preset, f)

    IRConfig.register_preset_dir(tmp_path)
    cfg = {"nested": "${preset:test2.json}"}
    cfg = Config(**cfg)
    assert cfg.nested.test == 2


def test_add_system_var():
    IRConfig.register_system_var("test", 123)
    var = IRConfig.get_system_var("test")
    assert var == 123


def test_system_from_file(tmp_path):
    system_vars = {
        "test": 2,
    }

    path = os.path.join(tmp_path, 'test2.json')
    with pytest.raises(FileNotFoundError):
        IRConfig.register_system_var_from_file(path)

    with open(path, 'w') as f:
        json.dump(system_vars, f)

    IRConfig.register_system_var_from_file(path)
    var = IRConfig.get_system_var("test")
    assert var == 2


def test_system_resolve():
    IRConfig.register_system_var("test", 123)
    cfg = {"test": "${system:test}"}
    cfg = NestedConfig(**cfg)
    assert cfg.test == 123
