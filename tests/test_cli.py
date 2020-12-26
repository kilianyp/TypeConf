from typeconf import BaseConfig, SelectConfig
import unittest.mock
from typing import Optional, List, Tuple
from pydantic import ValidationError
import pytest
import json
import os


class ConfigOptional(BaseConfig):
    test : int = 1
    test2 : Optional[int]


def test_optional():
    testargs = ["_", "--test", 2]
    with unittest.mock.patch('sys.argv', testargs):
        kwargs = ConfigOptional.parse_cli_args()
        cfg = ConfigOptional(**kwargs)
        assert cfg.test == 2

    testargs = ["_", "--test2", 2]
    with unittest.mock.patch('sys.argv', testargs):
        kwargs = ConfigOptional.parse_cli_args()
        cfg = ConfigOptional(**kwargs)
        assert cfg.test2 == 2


class ConfigPositional(BaseConfig):
    test1 : int
    test2 : int


@pytest.mark.xfail
def test_positional():
    testargs = ["_", "1", "2"]
    with unittest.mock.patch('sys.argv', testargs):
        kwargs = ConfigOptional.parse_cli_args()
        cfg = ConfigOptional(**kwargs)
        assert cfg.test1 == 1
        assert cfg.test2 == 2


class NestedNestedConfig(BaseConfig):
    test : int


class NestedConfig(BaseConfig):
    test : int
    nested : NestedNestedConfig


def test_nested():
    testargs = ["_", "--test", "123", "--nested.test", "456"]
    with unittest.mock.patch('sys.argv', testargs):
        kwargs = NestedConfig.parse_cli_args()
        cfg = NestedConfig(**kwargs)
        assert cfg.test == 123
        assert cfg.nested.test == 456


class TestConfig(BaseConfig):
    nested : NestedConfig


def test_nestednested():
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


class TupleIntConfig(BaseConfig):
    test : Tuple[int, int]


def test_tuple_int():
    testargs = ["_", "--test", "123", "456"]
    with unittest.mock.patch('sys.argv', testargs):
        kwargs = TupleIntConfig.parse_cli_args()
        cfg = TupleIntConfig(**kwargs)
        assert cfg.test == (123, 456)


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
        assert cfg.test == [3, 4]


@pytest.mark.xfail(reason="Fails because name is not known during cli parsing. Cannot know it's a list.")
def test_impossible_select_list_args():
    testargs = ["_", "--test", "3"]
    with unittest.mock.patch('sys.argv', testargs):
        kwargs = MasterConfig.parse_cli_args()
        kwargs.update({'name': 'slave2'})
        cfg = MasterConfig(**kwargs)
        assert cfg.test == [3]


class UnknownConfig(BaseConfig):
    pass


@pytest.mark.xfail(reason="Last case is not implemented")
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


def test_config_path(tmp_path):
    class NestedConfig(BaseConfig):
        test : int

    class NestedConfig2(BaseConfig):
        test : int = 1

    class Config(BaseConfig):
        nested : NestedConfig
        nested2 : NestedConfig2

    config = {
        "nested" : {
            "test": 1
        },
        "nested2" : {
            "test": 1
        }
    }

    path =  os.path.join(tmp_path, 'config.json')
    with open(path, 'w') as f:
        json.dump(config, f)

    testargs = ["_", '--config_path', path]
    with unittest.mock.patch('sys.argv', testargs):
        kwargs = Config.parse_cli_args()
        cfg = Config(**kwargs)
        assert cfg.nested.test == 1
        assert cfg.nested2.test == 1

    testargs = ["_", '--config_path', path, '--nested.test', '2', '--nested2.test', '2']
    with unittest.mock.patch('sys.argv', testargs):
        kwargs = Config.parse_cli_args()
        cfg = Config(**kwargs)
        assert cfg.nested.test == 2
        assert cfg.nested2.test == 2


def test_overwrite_default_from_config(tmp_path):
    class NestedConfig(BaseConfig):
        test : int = 1

    class Config(BaseConfig):
        nested : NestedConfig

    config = {
        "nested" : {
            "test": 2
        }
    }

    path = os.path.join(tmp_path, 'config.json')
    with open(path, 'w') as f:
        json.dump(config, f)

    testargs = ["_", '--config_path', path]
    with unittest.mock.patch('sys.argv', testargs):
        kwargs = Config.parse_cli_args()
        cfg = Config(**kwargs)
        assert cfg.nested.test == 2


def test_sorted():
    class Config(BaseConfig):
        test1: int
        test2: int
        test3: int
        test0: int
        a : int
        b : int
    keys = []
    for k, v in Config.__fields__.items():
        keys.append(k)
    assert keys == ['test1', 'test2', 'test3', 'test0', 'a', 'b']
