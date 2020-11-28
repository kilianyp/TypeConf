from typeconf import BaseConfig
import pytest
from pydantic import ValidationError

class Config(BaseConfig):
    pass

def test_unknown():
    with pytest.raises(ValidationError):
        Config.parse(**{"test": 1})


