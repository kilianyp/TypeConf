from typeconf.cli import Parser
import pytest


def test_to_argdict():
    args = ["--test", "123", "456", "--test2", "456"]
    arg_dict = Parser.arglist2dict(args)
    expected = {
        "test": ["123", "456"],
        "test2": ["456"]
    }
    assert arg_dict == expected


def test_flag():
    args = ["--test"]
    with pytest.raises(ValueError):
        Parser.arglist2dict(args)


def test_update_dict():
    argdict = {}
    Parser.update_arg_dict(argdict, 'a', None)
    with pytest.raises(ValueError):
        Parser.update_arg_dict(argdict, 'a.b', None)
    Parser.update_arg_dict(argdict, 'b.c.d', None)
    assert argdict == {"b": {"c": {"d": None}}, "a": None}


def test_nested_to_argdict():
    args = ["--nested.test", "123", "456" ]
    arg_dict = Parser.arglist2dict(args)
    expected = {
        "nested": {
            "test": ["123", "456"]
        }
    }
    assert arg_dict == expected


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


def test_incomplete(parser):
    parser.add_argument('--test', help="")
    with pytest.raises(ValueError):
        args = parser.parse_args(["--test"])

    with pytest.raises(ValueError):
        args = parser.parse_args(["--test 2 --test2"])


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
    assert 'test' in parser._subparsers
    args = parser.parse_args(['--test.test', '2'])
    assert args == {"test": {"test": "2"}}


def test_istlisttype():
    from typeconf.cli import islisttype
    from typing import List, Optional

    assert islisttype(List) == True
    assert islisttype(List[int]) == True
    assert islisttype(List[str]) == True
    assert islisttype(Optional[List]) == True
    assert islisttype(Optional[List[int]]) == True
    assert islisttype(str) == False
    assert islisttype(int) == False


def test_isttupletype():
    from typeconf.cli import istupletype
    from typing import Tuple, Optional

    assert istupletype(Tuple) == True
    assert istupletype(Tuple[int]) == True
    assert istupletype(Tuple[str]) == True
    assert istupletype(Optional[Tuple]) == True
    assert istupletype(Optional[Tuple[int]]) == True
    assert istupletype(str) == False
    assert istupletype(int) == False


def test_subparser():
    parser = Parser()
    parser.add_argument('--test')
    subparser = Parser()
    subparser.add_argument('--test')
    parser.add_subparser(subparser, 'nested')
    args = parser.parse_args(['--test', '1', '--nested.test', '2'])
    assert args == {'test': '1', 'nested': {'test': '2'}}


def test_nested_select_parser():
    from typeconf import BaseConfig, SelectConfig

    class ParentConfig(SelectConfig):
        pass

    @ParentConfig.register('child')
    class ChildConfig(ParentConfig):
        test : int = 1

    class Config(BaseConfig):
        test : ParentConfig


    parser = Parser.from_config(Config)
    args = parser.parse_args(['--test.test', '2'])
    assert args == {"test": {"test": "2"}}


@pytest.mark.xfail(reason="Not supported")
def test_overwrite_preset():
    parser = Parser()
    subparser = Parser()
    subparser.add_argument('--test')
    parser.add_subparser(subparser, 'nested')
    args = parser.parse_args(['--nested.test', '2', '--nested', '${preset:test}'])
    args = parser.parse_args(['--nested', '${preset:test}', '--nested.test', '2'])
