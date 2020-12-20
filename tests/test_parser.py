from typeconf.cli import Parser
import pytest


@pytest.fixture
def parser():
    return Parser()


def test_basic(parser):
    parser.add_argument('--test', help="")
    args = parser.parse_args(["--test", "2"])
    assert args == {"test": "2"}


def test_basic2(parser):
    parser.add_argument('--test2', help="")
    args = parser.parse_args(["--test2", "2"])
    assert args == {"test2": "2"}


def test_basic3(parser):
    parser.add_argument('--test', help="")
    parser.add_argument('--test2', help="")
    args = parser.parse_args(["--test", "1", "--test2", "2"])
    assert args == {"test": "1", "test2": "2"}


def test_prefix(parser):
    with pytest.raises(ValueError):
        parser.add_argument('-test', help="")


def test_unknown(parser):
    with pytest.raises(ValueError):
        args = parser.parse_args(["--test"])


def test_list(parser):
    parser.add_argument('--test', help="", type="list")
    args = parser.parse_args(["--test", "1", "2"])
    assert args == {"test": ["1", "2"]}


def test_double_dest(parser):
    parser.add_argument('--test', help="", type="list")
    with pytest.raises(ValueError):
        parser.add_argument('--test', help="", type="default")


def test_list_with_default(parser):
    parser.add_argument('--test', help="", type="list")
    parser.add_argument('--test2', help="", type="default")
    args = parser.parse_args(["--test", "1", "2"])
    assert args == {"test": ["1", "2"]}


def test_unused(parser):
    parser.add_argument('--test', help="")
    args = parser.parse_args([])
    assert args == {}


def test_positional(parser):
    parser.add_argument('--test', help="")
    with pytest.raises(ValueError):
        args = parser.parse_args(["test", "1"])


def test_parser_from_config():
    from typeconf import BaseConfig

    class Config(BaseConfig):
        test : int
        test2 : int

    parser = Parser.from_config(Config)
    assert 'test' in parser._actions
    assert 'test2' in parser._actions


def test_nested_parser():
    from typeconf import BaseConfig

    class NestedConfig(BaseConfig):
        test : int
    class Config(BaseConfig):
        test : NestedConfig


    parser = Parser.from_config(Config)
    assert 'test.test' in parser._actions
    args = parser.parse_args(['--test.test', '2'])
    assert args == {"test": {"test": "2"}}

def test_istlisttype():
    from typeconf import BaseConfig
    from typeconf.cli import islisttype
    from typing import List, Optional

    assert islisttype(List) == True
    assert islisttype(List[int]) == True
    assert islisttype(List[str]) == True
    assert islisttype(Optional[List]) == True
    assert islisttype(Optional[List[int]]) == True
    assert islisttype(str) == False
    assert islisttype(int) == False
