from collections import defaultdict
from pydantic import BaseModel
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class BaseConfig(BaseModel):
    """
    https://github.com/samuelcolvin/pydantic/issues/2130
    """
    _field_access = defaultdict(int)

    class Config:
        underscore_attrs_are_private = True

    def __getattribute__(self, item):
        if not item.startswith('_') and item in self.__fields__:
            self._field_access[item] += 1
        return super().__getattribute__(item)

    def get_stats(self) -> Dict[str, int]:
        return dict(self._field_access)

    def find_unused(self):
        return set(self.__fields__.keys()) - set(self._field_access.keys())

    @classmethod
    def build_config(cls, *args, **kwargs):
        return cls

    @classmethod
    def parse(cls, cfg, *args, **kwargs):
        cls = cls.build_config(cfg, *args, **kwargs)
        return cls(**cfg)


class SelectConfig(BaseConfig):
    name : str

    @classmethod
    def register(cls, name):
        def _register(cls):
            cls._registered[name] = cls
            logger.debug(cls._registered)
            return cls
        return _register

    @classmethod
    def build_config(cls, cfg):
        if 'name' not in cfg:
            raise ValueError("Select builder expects a config with name: %s", cfg)

        name = cfg['name']
        cls = cls._registered[name]
        return cls.build_config(cfg)

    def build(self, cfg, *args, **kwargs):
        raise RuntimeError("This method must be overwritten by selected option")

# Work around. Cannot set it directly in the class, causes
# "Cannot set member"
SelectConfig._registered = {}
