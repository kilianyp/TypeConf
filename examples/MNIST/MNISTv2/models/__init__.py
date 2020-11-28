from typeconf import SelectConfig
from typing import Optional
from pydantic import FilePath
from abc import abstractmethod


class ModelConfig(SelectConfig):
    weights : Optional[FilePath]

    def build(self, *args, **kwargs):
        model = self._build(*args, **kwargs)
        return model

    @abstractmethod
    def _build(self, *args, **kwargs):
        pass

from . import net
