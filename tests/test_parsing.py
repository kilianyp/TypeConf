from typeconf import BaseConfig
import pytest
from pydantic import ValidationError
import unittest.mock
from typing import Callable


class Config(BaseConfig):
    pass


def test_unknown():
    with pytest.raises(ValidationError):
        Config(**{"test": 1})


class Config2(BaseConfig):
    test1: int = 0
    test2: int


class Config3(BaseConfig):
    nested : Config2


@pytest.mark.xfail(rason="Not implemented")
def test_nested_but_no_overlap():
    testargs = ["_", "--nested.test1", "1"]
    with unittest.mock.patch('sys.argv', testargs):
        kwargs = Config3.parse_cli_args()
        kwargs.update({"nested": {"test2": 2}})
        cfg = Config3(**kwargs)
        assert cfg.nested.test1 == 1
        assert cfg.nested.test2 == 2


def test_but_no_overlap():
    testargs = ["_", "--test1", "1"]
    with unittest.mock.patch('sys.argv', testargs):
        kwargs = Config2.parse_cli_args()
        kwargs.update({"test2": 2})
        cfg = Config2(**kwargs)
        assert cfg.test1 == 1
        assert cfg.test2 == 2


class ConfigCallable(BaseConfig):
    fn : Callable


def test_callable():
    import torch
    fn = torch.relu
    cfg = ConfigCallable(fn=fn)
    print(cfg)
