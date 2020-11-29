from collections import defaultdict
import argparse
from pydantic import BaseModel, Extra, create_model, ValidationError
from typing import Dict, ClassVar
from abc import abstractmethod
import logging
import inspect


logger = logging.getLogger(__name__)


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


def fields2args(parser, fields, prefix='', in_select_class=False, choices=[]):
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

        if in_select_class and key == "name":
            parser.add_argument(
                f'--{prefix}{f.name}',
                default=f.default,
                choices=choices
            )
        elif inspect.isclass(f.outer_type_) and issubclass(f.outer_type_, BaseConfig):
            if issubclass(f.outer_type_, SelectConfig):
                in_select_class = True
                choices = list(f.outer_type_._registered.keys())
            else:
                in_select_class = False
                choices = []
            # TODO add groups
            fields2args(
                parser,
                f.outer_type_.__fields__,
                prefix + f.name + '.',
                in_select_class,
                choices=choices)
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


def read_file_cfg(path):
    if path.endswith('.json'):
        import json
        with open(path, 'r') as f:
            return json.load(f)
    if path.endswith('.yaml'):
        # TODO requires extra dependency
        raise NotImplementedError
    if path.endswith('.py'):
        content = open(path).read()
        # https://stackoverflow.com/questions/1463306/how-does-exec-work-with-locals
        ldict = {}
        exec(content, globals(), ldict)
        return ldict['cfg']

    raise ValueError("Unknown file format %s" % path)


class BaseConfig(BaseModel):
    """
    https://github.com/samuelcolvin/pydantic/issues/2130
    """
    _field_access = defaultdict(int)

    # TODO what happens when using multipe classes
    _parser : ClassVar = None

    class Config:
        underscore_attrs_are_private = True
        extra = Extra.forbid

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __new__(cls, **kwargs):
        cls = cls.build_config(kwargs)
        obj = super().__new__(cls)
        return obj

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
                    raise ValueError("%s was not found in cfg" % key)
                config = f.outer_type_.build_config(cfg[key])
                # pydantic needs the ellipsis
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
    def parse_cli_args(cls):
        if cls._parser is None:
            parser = argparse.ArgumentParser(cls.__name__)
            parser.add_argument('--config_path')
            cls._parser = fields2args(parser, cls.__fields__)
        cli_args, unknown_args = cls._parser.parse_known_args()
        args = cli_args.__dict__
        config_path = args.pop('config_path')

        if config_path is not None:
            kwargs = read_file_cfg(config_path)
        else:
            kwargs = {}

        # Here needs to be the priority
        # args over cfg
        kwargs.update(args2dict(args))
        r = list2dict(unknown_args)
        kwargs.update(r)
        return kwargs


class SelectConfig(BaseConfig):
    name : str
    _registered : ClassVar[Dict] = None

    @classmethod
    def register(cls, name):
        """
        Register a config.
        Namespace is per class.
        """
        if cls._registered is None:
            cls._registered = {}

        def _register(cls):
            if cls._registered is None:
                raise RuntimeError("Make sure to inherit from register class")

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
