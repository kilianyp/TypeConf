from typeconf import BaseConfig
import pytest
from pydantic import ValidationError
import logging


class Config(BaseConfig):
    pass


def test_no_init(caplog):
    with caplog.at_level(logging.WARNING):
        Config()
    assert len(caplog.text) > 0


def test_unknown():
    with pytest.raises(ValidationError):
        Config.parse(**{"test": 1})


