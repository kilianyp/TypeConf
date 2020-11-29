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
    with unittest.mock.patch('sys.argv', testargs):
        kwargs = TestConfig.parse_cli_args()
        cfg = TestConfig(**kwargs)
        assert cfg.nested.test == 123
        assert cfg.nested.nested.test == 456


class ListConfig(BaseConfig):
    test : List


def test_list_1param():
    testargs = ["_", "--test", "123"]
    with unittest.mock.patch('sys.argv', testargs):
        kwargs = ListIntConfig.parse_cli_args()
        cfg = ListConfig(**kwargs)
        assert cfg.test == ["123"]


def test_list_2param():
    testargs = ["_", "--test", "123", "456"]
    with unittest.mock.patch('sys.argv', testargs):
        kwargs = ListIntConfig.parse_cli_args()
        cfg = ListConfig(**kwargs)
        assert cfg.test == ["123", "456"]


class ListIntConfig(BaseConfig):
    test : List[int]


def test_list_int():
    testargs = ["_", "--test", "123", "456"]
    with unittest.mock.patch('sys.argv', testargs):
        kwargs = ListIntConfig.parse_cli_args()
        cfg = ListIntConfig(**kwargs)
        assert cfg.test == [123, 456]


class OptionalConfig(BaseConfig):
    test : Optional[str]


def test_optional():
    testargs = ["_"]
    with unittest.mock.patch('sys.argv', testargs):
        kwargs = OptionalConfig.parse_cli_args()
        cfg = OptionalConfig(**kwargs)
        assert cfg.test is None


class ListOptionalConfig(BaseConfig):
    test : Optional[List[int]]


def test_optional_list_int():
    with unittest.mock.patch('sys.argv', ["_"]):
        kwargs = ListOptionalConfig.parse_cli_args()
        cfg = ListOptionalConfig(**kwargs)
        assert cfg.test is None

    testargs = ["_", "--test", "123", "456"]
    with unittest.mock.patch('sys.argv', testargs):
        kwargs = ListOptionalConfig.parse_cli_args()
        cfg = ListOptionalConfig(**kwargs)
        assert cfg.test == [123, 456]


class BoolConfig(BaseConfig):
    flag_true : bool = False
    flag_false: bool = True


def test_bool_flag():
    testargs = ["_", "--flag_true", "--flag_false"]
    with unittest.mock.patch('sys.argv', testargs):
        kwargs = BoolConfig.parse_cli_args()
        cfg = BoolConfig(**kwargs)
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
        kwargs = MasterConfig.parse_cli_args()
        kwargs.update({'name': 'slave1'})
        cfg = MasterConfig(**kwargs)
        assert cfg.test == 3


@MasterConfig.register('slave2')
class SlaveConfig(MasterConfig):
    test : List[int]
    def build(self):
        pass


def test_select_list_args():
    testargs = ["_", "--test", "3", "4"]
    with unittest.mock.patch('sys.argv', testargs):
        kwargs = MasterConfig.parse_cli_args()
        kwargs.update({'name': 'slave2'})
        cfg = MasterConfig(**kwargs)
        assert cfg.test == ["3", "4"]


class UnknownConfig(BaseConfig):
    pass


def test_unknown():
    testargs = ["_", "--flag", "1"]
    with unittest.mock.patch('sys.argv', testargs):
        with pytest.raises(ValidationError):
            kwargs = UnknownConfig.parse_cli_args()
            cfg = UnknownConfig(**kwargs)

    testargs = ["_", "--flag", "1", "2"]
    with unittest.mock.patch('sys.argv', testargs):
        with pytest.raises(ValidationError):
            kwargs = UnknownConfig.parse_cli_args()
            cfg = UnknownConfig(**kwargs)

    testargs = ["_", "--flag"]
    with unittest.mock.patch('sys.argv', testargs):
        with pytest.raises(ValidationError):
            kwargs = UnknownConfig.parse_cli_args()
            cfg = UnknownConfig(**kwargs)

