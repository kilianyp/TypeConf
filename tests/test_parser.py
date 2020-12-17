from typeconf.cli import Parser
import unittest.mock
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


def test_list(parser):
    parser.add_argument('--test', help="")
    args = parser.parse_args(["--test", "1", "2"])
    assert args == {"test": ["1", "2"]}


def test_flag(parser):
    parser.add_argument('--test', action="store_true", help="")
    args = parser.parse_args(["--test"])
    assert args == {"test": True}


def test_unused(parser):
    parser.add_argument('--test', help="")
    args = parser.parse_args([])
    assert args == {}


def test_positional(parser):
    parser.add_argument('--test', help="")
    with pytest.raises(ValueError):
        args = parser.parse_args(["test", "1"])

