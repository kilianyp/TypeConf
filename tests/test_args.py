from typeconf import BaseConfig
import unittest.mock
from typing import Optional, List


class NestedNestedConfig(BaseConfig):
    test : int

class NestedConfig(BaseConfig):
    test : int
    nested : NestedNestedConfig


class TestConfig(BaseConfig):
    nested : NestedConfig

def test_nested():
    testargs = ["_", "--nested.test", "123", "--nested.nested.test", "456"]
    TestConfig.use_cli()
    with unittest.mock.patch('sys.argv', testargs):
        cfg = TestConfig()
        assert cfg.nested.test == 123
        assert cfg.nested.nested.test == 456



class ListConfig(BaseConfig):
    test : List


def test_list_1param():
    testargs = ["_", "--test", "123"]
    ListConfig.use_cli()
    with unittest.mock.patch('sys.argv', testargs):
        cfg = ListConfig()
        assert cfg.test == ["123"]


def test_list_2param():
    testargs = ["_", "--test", "123", "456"]
    ListConfig.use_cli()
    with unittest.mock.patch('sys.argv', testargs):
        cfg = ListConfig()
        assert cfg.test == ["123", "456"]


class ListIntConfig(BaseConfig):
    test : List[int]


def test_list_int():
    testargs = ["_", "--test", "123", "456"]
    ListIntConfig.use_cli()
    with unittest.mock.patch('sys.argv', testargs):
        cfg = ListIntConfig()
        assert cfg.test == [123, 456]

class OptionalConfig(BaseConfig):
    test : Optional[str]

def test_optional():
    testargs = ["_"]
    OptionalConfig.use_cli()
    with unittest.mock.patch('sys.argv', testargs):
        cfg = OptionalConfig()
        assert cfg.test is None


class ListOptionalConfig(BaseConfig):
    test : Optional[List[int]]


def test_optional_list_int():
    ListOptionalConfig.use_cli()
    with unittest.mock.patch('sys.argv', ["_"]):
        cfg = ListOptionalConfig()
        cfg.test == []

    testargs = ["_", "--test", "123", "456"]
    with unittest.mock.patch('sys.argv', testargs):
        cfg = ListOptionalConfig()
        assert cfg.test == [123, 456]


class BoolConfig(BaseConfig):
    flag_true : bool = False
    flag_false: bool = True



def test_bool_flag():
    BoolConfig.use_cli()
    testargs = ["_", "--flag_true", "--flag_false"]
    with unittest.mock.patch('sys.argv', testargs):
        cfg = BoolConfig()
        assert cfg.flag_true
        assert not cfg.flag_false
