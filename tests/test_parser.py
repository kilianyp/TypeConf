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

def test_unkown(parser):
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

