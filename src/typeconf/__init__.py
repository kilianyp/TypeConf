from collections import defaultdict
from pydantic import BaseModel, Extra, create_model, ValidationError
from typing import Dict, ClassVar
import logging
import inspect
from typing import Tuple
from .irconfig import IRConfig
from .utils import read_file_cfg


logger = logging.getLogger(__name__)


def resolve(fn):
    """
    Resolves the arguments before running

    TODO this is called multiple times, twice per BaseConfig
    For a nested config, will be called twice everytime for every nesting
    even though once is enough.
    """
    def wrapper(*args, **kwargs):
        cfg = IRConfig.create(kwargs)
        cfg = IRConfig.to_container(cfg, resolve=True)
        return fn(*args, **cfg)
    return wrapper


def partial_dict_update(dict1, dict2):
    """
    dict1 is updated with dict2

    Args:
        dict1 (dict)
        dict2 (dict)
    """
    for key, value in dict2.items():
        if key in dict1:
            if isinstance(dict1[key], dict) and isinstance(value, dict):
                partial_dict_update(dict1[key], value)
            else:
                dict1[key] = value
        else:
            dict1[key] = value


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

    @resolve
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @resolve
    def __new__(cls, **kwargs):
        cls = cls.build_config(kwargs)
        obj = super().__new__(cls)
        return obj

    def __getattribute__(self, item):
        if not item.startswith('_') and item in self.__fields__:
            self._field_access[item] += 1
        return super().__getattribute__(item)

    def __getitem__(self, item):
        return self.__getattribute__(item)

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
                    # can also be optional
                    if f.allow_none:
                        continue
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
    def _create_parser(cls):
        from typeconf import cli
        parser = cli.Parser.from_config(cls)
        parser.add_argument('--config_path')
        parser.add_argument('--presets')
        parser.add_argument('--system')
        return parser

    @classmethod
    def register_system_var_from_file(cls, path):
        IRConfig.register_system_var_from_file(path)

    @classmethod
    def parse_cli_args(cls):
        if cls._parser is None:
            cls._parser = cls._create_parser()
        args = cls._parser.parse_args()
        # Special arguments
        config_path = args.get('config_path')
        preset_dir = args.get('presets')
        system_path = args.get('system')

        if config_path is not None:
            kwargs = read_file_cfg(config_path)
            args.pop('config_path')
        else:
            kwargs = {}

        if preset_dir is not None:
            from .irconfig import IRConfig
            IRConfig.register_preset_dir(preset_dir)
            args.pop('presets')

        if system_path is not None:
            from .irconfig import IRConfig
            IRConfig.register_system_var_from_file(system_path)
            args.pop('system')
            print(args)

        # Here needs to be the priority
        # args over cfg
        partial_dict_update(kwargs, args)
        return kwargs


def all_lower(string):
    return string.lower()


class SelectConfig(BaseConfig):
    name : str
    _registered : ClassVar[Dict] = None
    _sanitize_fn : ClassVar[callable] = all_lower

    @classmethod
    def register(cls, *names : Tuple[str]):
        """
        Register a config.
        Namespace is per class.
        """
        if cls._registered is None:
            cls._registered = {}

        def _register(obj):
            if not inspect.isclass(obj):
                raise RuntimeError("Only supporting classes")
            if obj.__bases__ != (cls, ):
                raise RuntimeError("Please inherit and register from the parent config class")

            for name in names:
                if cls._sanitize_fn(name) in cls._registered:
                    raise ValueError("%s has already been registered: %s" % (name, cls._registered[name]))
                cls._registered[cls._sanitize_fn(name)] = obj
            logger.debug(cls._registered)
            return obj
        return _register

    @classmethod
    def build_config(cls, cfg):
        name = cfg.get('name')
        if name is None:
            raise ValueError("Select builder expects a config with name set: %s" % cfg)

        name = cls._sanitize_fn(cfg['name'])

        if name not in cls._registered:
            raise ValueError("Unknown option for %s: %s" % (cls.__name__, cfg['name']))
        cls = cls._registered[name]
        return cls._build_config(cfg)

    @classmethod
    def _build_config(cls, cfg):
        return cls

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
