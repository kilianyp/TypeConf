from pydantic import BaseModel
import argparse
from typing import List, Optional
import ipdb
import inspect


def fields2args(parser, fields, prefix=''):
    """
    Avoids any parsing functionality --> all optional

    args:
        fields: Pydantic fields
    """
    for key, f in fields.items():
        if f.outer_type_ == List:
            nargs = '+'
        else:
            nargs = None

        if inspect.isclass(f.outer_type_) and issubclass(f.outer_type_, ArgConfig):
            fields2args(parser, f.outer_type_.__fields__, f.name + '.')
        else:
            parser.add_argument(f'--{prefix}{f.name}', default=f.default, nargs=nargs)
    return parser


def read_cfg(path):
    return {}


class ArgConfig(BaseModel):
    _parser = None

    class Config:
        underscore_attrs_are_private = True

    def __init__(self, **kwargs):
        if self._parser is not None:
            cli_args = self._parser.parse_args()
            file_cfg = read_cfg(cli_args.config_path)
            # Here needs to be the priority
            # args over cfg
            # what about runtime arguments
            # TODO deal with points
            file_cfg.update(cli_args.__dict__)
            # TODO update recursively
            file_cfg.update(kwargs)
            kwargs = file_cfg
        super().__init__(**kwargs)


    @classmethod
    def use_cli(cls):
        parser = argparse.ArgumentParser(cls.__name__)
        parser.add_argument('--config_path')
        print(cls)
        cls._parser = fields2args(parser, cls.__fields__)



class NestedConfig(ArgConfig):
    test : int



class TestConfig(ArgConfig):
    test : int
    test2 : Optional[List]
    nested : NestedConfig


if __name__ == "__main__":
    TestConfig.use_cli()
    cfg = TestConfig()
    print(cfg)
