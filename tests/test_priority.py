from typeconf import BaseConfig, partial_dict_update
import unittest.mock
import json


def test_partial_dict_update():
    cfg1 = {
        "test": 1,
        "nested": {
            "test1": 1,
            "test2": 2
        }
    }
    cfg2 = {
        "test2": 2,
        "nested": {
            "test2": 3,
        }
    }

    partial_dict_update(cfg1, cfg2)
    result = {
        "test": 1,
        "nested": {
            "test1": 1,
            "test2": 3
        },
        "test2": 2,
    }
    assert cfg1 == result
    assert cfg1['nested']['test2'] == 3
    assert cfg1['nested']['test1'] == 1


class NestedConfig(BaseConfig):
    test1 : int = 1
    test2 : int = 2


class Config(BaseConfig):
    test : int = 1
    nested : NestedConfig = NestedConfig()


def test_cli_over_config(tmp_path):
    config = {
        "test": 2
    }
    cfg_file = tmp_path / "config.json"

    with open(cfg_file, 'w') as f:
        json.dump(config, f)

    with unittest.mock.patch('sys.argv', ['_', '--test', '3', '--config_path', str(cfg_file)]):
        kwargs = Config.parse_cli_args()
        assert kwargs['test'] == '3'


def test_nested_cli_over_config(tmp_path):
    config = {
        "nested": {
            "test1": 2
        }
    }
    cfg_file = tmp_path / "config.json"

    with open(cfg_file, 'w') as f:
        json.dump(config, f)

    with unittest.mock.patch('sys.argv', ['_', '--nested.test1', '3', '--config_path', str(cfg_file)]):
        kwargs = Config.parse_cli_args()
        assert kwargs['nested']['test1'] == '3'

    with unittest.mock.patch('sys.argv', ['_', '--nested.test2', '3', '--config_path', str(cfg_file)]):
        kwargs = Config.parse_cli_args()
        # TODO fails because of default keyword overwriting config
        # Refactor parser
        assert kwargs['nested']['test1'] == '2'
        assert kwargs['nested']['test2'] == '3'
