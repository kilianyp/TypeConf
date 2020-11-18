from collections import defaultdict
from pydantic import BaseModel
from typing import Dict


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


# bind together building object, building config and config object
# folder pytorch
# folder optimizer
# how to subclass
# select a specific class by name

class BaseBuilder(object):
    def build_config(self, cfg):
        pass

    def build_object(self, cfg, *args, **kwargs):
        pass

    def parse(self, cfg):
        Model = self.build_config(cfg)
        return Model(**cfg)


class SelectBuilder(BaseBuilder):
    registered = {}

    @classmethod
    def register(cls, name):
        def _register(cls):
            cls.registered[name] = cls
            return cls
        return _register

    def build_config(self, cfg):
        if 'name' not in cfg:
            raise ValueError("Select builder expects a config with name: %s", cfg)

        name = cfg['name']
        cls = self.registered[name]
        return cls().build_config(cfg)

    def build_object(self, cfg, *args, **kwargs):
        raise RuntimeError("This method must be overwritten by selected option")

