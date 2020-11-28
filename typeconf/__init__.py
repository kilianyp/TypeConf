from collections import defaultdict
import argparse
from pydantic import BaseModel, Extra, create_model, ValidationError
from typing import Dict
from abc import abstractmethod
import logging
import inspect


logger = logging.getLogger(__name__)


def fields2args(parser, fields, prefix=''):
    """
    Avoids any parsing functionality --> all optional

    args:
        fields: Pydantic fields
        parser: ArgumentParser
    """
    for key, f in fields.items():
        # TODO check for annotation
        # Work around
        if not inspect.isclass(f.outer_type_) and f.outer_type_.__origin__ == list:
            # if its not a class, it's probably an annotation instance
            nargs = '+'
        else:
            nargs = None

        if f.outer_type_ == bool and f.default is not None:
            if f.default:
                action = 'store_false'
            else:
                action = 'store_true'
        else:
            action = None

        if inspect.isclass(f.outer_type_) and issubclass(f.outer_type_, BaseConfig):
            # TODO add groups
            fields2args(parser, f.outer_type_.__fields__, prefix + f.name + '.')
            # TODO this is necessary because otherwise
            # when instantiating the sub config it will complain
            # AttributeError: _parser
            # ALternative would be that each class parses it's own arguments
            f.outer_type_._parser = None
        else:
            # TODO for required set special default value that can be ignored later
            # to get later proper error value
            if action is not None:
                parser.add_argument(
                        f'--{prefix}{f.name}',
                        default=f.default,
                        action=action)
            else:
                parser.add_argument(
                        f'--{prefix}{f.name}',
                        default=f.default,
                        nargs=nargs)

    return parser


class BaseConfig(BaseModel):
    """
    https://github.com/samuelcolvin/pydantic/issues/2130
    """
    _field_access = defaultdict(int)

    class Config:
        underscore_attrs_are_private = True
        extra = Extra.forbid

    def __init__(self, **kwargs):
        # TODO can we check if this was called without parse at first
        super().__init__(**kwargs)

    def __getattribute__(self, item):
        if not item.startswith('_') and item in self.__fields__:
            self._field_access[item] += 1
        return super().__getattribute__(item)

    def get_stats(self) -> Dict[str, int]:
        stats = dict(self._field_access)

        for name, field in self.__fields__.items():
            # don't track
            f = super().__getattribute__(name)
            if isinstance(f, BaseConfig):
                sub_stats = f.get_stats()
                def flatten(d):
                    for key, value in d.items():
                        stats[field.name + '.' + key] = value
                flatten(sub_stats)
        return stats

    def find_unused(self):
        return set(self.__fields__.keys()) - set(self._field_access.keys())

    @classmethod
    def build_config(cls, cfg):
        dynamic_configs = {}
        for key, f in cls.__fields__.items():
            if inspect.isclass(f.outer_type_) and issubclass(f.outer_type_, SelectConfig):
                if key not in cfg:
                    raise ValidationError()
                config = f.outer_type_.build_config(cfg[key])
                dynamic_configs[key] = (config, ...)

        if len(dynamic_configs) > 0:
            return create_model(
                cls.__name__,
                __base__=cls,
                **dynamic_configs
            )
        else:
            return cls

    @classmethod
    def parse(cls, **kwargs):
        if cls._parser is not None:
            cli_args, unknown_args = cls._parser.parse_known_args()
            # file_cfg = read_cfg(cli_args.config_path)
            file_cfg = {}
            # Here needs to be the priority
            # args over cfg
            # what about runtime arguments

            def args2dict(dic):
                r = {}
                for key, value in dic.items():
                    depth = key.split('.')
                    cur = r
                    for idx, d in enumerate(depth):
                        if idx == len(depth) - 1:
                            cur[d] = value
                        else:
                            if d not in cur:
                                cur[d] = {}
                            cur = cur[d]
                return r

            def list2dict(li):
                dic = {}
                for l in li:
                    if l.startswith('--'):
                        name = l[2:]
                    else:
                        dic[name] = l
                return dic

            args = cli_args.__dict__
            args.pop('config_path')
            file_cfg.update(args2dict(args))
            r = list2dict(unknown_args)
            file_cfg.update(r)
            # TODO update fields individually
            file_cfg.update(kwargs)
            kwargs = file_cfg
        cls = cls.build_config(kwargs)
        return cls(**kwargs)

    @classmethod
    def use_cli(cls):
        parser = argparse.ArgumentParser(cls.__name__)
        parser.add_argument('--config_path')
        cls._parser = fields2args(parser, cls.__fields__)


# TODO what happens when using multipe classes
BaseConfig._parser = None


class SelectConfig(BaseConfig):
    name : str

    @classmethod
    def register(cls, name):
        def _register(cls):
            if name.lower() in cls._registered:
                raise ValueError("%s has already been registered: %s" % (name, cls._registered[name]))
            cls._registered[name.lower()] = cls
            logger.debug(cls._registered)
            return cls
        return _register

    @classmethod
    def build_config(cls, cfg):
        name = cfg.get('name')
        if name is None:
            raise ValueError("Select builder expects a config with name set: %s" % cfg)

        name = cfg['name'].lower()

        if name not in cls._registered:
            raise ValueError("Unknown option for %s: %s" % (cls.__name__, cfg['name']))
        cls = cls._registered[name]
        return cls._build_config(cfg)

    @classmethod
    def _build_config(cls, cfg):
        return cls

    @abstractmethod
    def build(self, cfg, *args, **kwargs):
        pass


# Work around. Cannot set it directly in the class, causes
# "Cannot set member"
SelectConfig._registered = {}
