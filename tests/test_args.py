from typeconf import BaseConfig, SelectConfig
import unittest.mock
from typing import Optional, List
from pydantic import ValidationError
import pytest


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
        cfg = TestConfig.parse()
        assert cfg.nested.test == 123
        assert cfg.nested.nested.test == 456


class ListConfig(BaseConfig):
    test : List


def test_list_1param():
    testargs = ["_", "--test", "123"]
    ListConfig.use_cli()
    with unittest.mock.patch('sys.argv', testargs):
        cfg = ListConfig.parse()
        assert cfg.test == ["123"]


def test_list_2param():
    testargs = ["_", "--test", "123", "456"]
    ListConfig.use_cli()
    with unittest.mock.patch('sys.argv', testargs):
        cfg = ListConfig.parse()
        assert cfg.test == ["123", "456"]


class ListIntConfig(BaseConfig):
    test : List[int]


def test_list_int():
    testargs = ["_", "--test", "123", "456"]
    ListIntConfig.use_cli()
    with unittest.mock.patch('sys.argv', testargs):
        cfg = ListIntConfig.parse()
        assert cfg.test == [123, 456]


class OptionalConfig(BaseConfig):
    test : Optional[str]


def test_optional():
    testargs = ["_"]
    OptionalConfig.use_cli()
    with unittest.mock.patch('sys.argv', testargs):
        cfg = OptionalConfig.parse()
        assert cfg.test is None


class ListOptionalConfig(BaseConfig):
    test : Optional[List[int]]


def test_optional_list_int():
    ListOptionalConfig.use_cli()
    with unittest.mock.patch('sys.argv', ["_"]):
        cfg = ListOptionalConfig.parse()
        cfg.test == []

    testargs = ["_", "--test", "123", "456"]
    with unittest.mock.patch('sys.argv', testargs):
        cfg = ListOptionalConfig.parse()
        assert cfg.test == [123, 456]


class BoolConfig(BaseConfig):
    flag_true : bool = False
    flag_false: bool = True


def test_bool_flag():
    BoolConfig.use_cli()
    testargs = ["_", "--flag_true", "--flag_false"]
    with unittest.mock.patch('sys.argv', testargs):
        cfg = BoolConfig.parse()
        assert cfg.flag_true
        assert not cfg.flag_false


class MasterConfig(SelectConfig):
    pass


@MasterConfig.register('slave1')
class SlaveConfig(MasterConfig):
    test : int
    def build(self):
        pass


def test_select_args():
    testargs = ["_", "--test", "3"]
    with unittest.mock.patch('sys.argv', testargs):
        MasterConfig.use_cli()
        cfg = MasterConfig.parse(**{'name': 'slave1'})
        assert cfg.test == 3


@MasterConfig.register('slave2')
class SlaveConfig(MasterConfig):
    test : List[int]
    def build(self):
        pass


def test_select_list_args():
    testargs = ["_", "--test", "3", "4"]
    with unittest.mock.patch('sys.argv', testargs):
        MasterConfig.use_cli()
        cfg = MasterConfig.parse(**{'name': 'slave2'})
        assert cfg.test == ["3", "4"]


class UnknownConfig(BaseConfig):
    pass


def test_unknown():
    UnknownConfig.use_cli()
    testargs = ["_", "--flag", "1"]
    with unittest.mock.patch('sys.argv', testargs):
        with pytest.raises(ValidationError):
            cfg = UnknownConfig.parse()

    testargs = ["_", "--flag", "1", "2"]
    with unittest.mock.patch('sys.argv', testargs):
        with pytest.raises(ValidationError):
            cfg = UnknownConfig.parse()

    testargs = ["_", "--flag"]
    with unittest.mock.patch('sys.argv', testargs):
        with pytest.raises(ValidationError):
            cfg = UnknownConfig.parse()

