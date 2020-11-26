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
            # TODO add groups
            fields2args(parser, f.outer_type_.__fields__, prefix + f.name + '.')
            # TODO this is necessary because otherwise 
            # when instantiating the sub config it will complain
            # AttributeError: _parser
            # ALternative would be that each class parses it's own arguments
            f.outer_type_._parser = None
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

            r = args2dict(cli_args.__dict__)
            file_cfg.update(r)
            # TODO update fields individually
            file_cfg.update(kwargs)
            kwargs = file_cfg
        super().__init__(**kwargs)


    @classmethod
    def use_cli(cls):
        parser = argparse.ArgumentParser(cls.__name__)
        parser.add_argument('--config_path')
        cls._parser = fields2args(parser, cls.__fields__)


# TODO test this
class NestedNestedConfig(ArgConfig):
    test : int

class NestedConfig(ArgConfig):
    test : int
    nested : NestedNestedConfig


class TestConfig(ArgConfig):
    test : int
    test2 : Optional[List]
    nested : NestedConfig


if __name__ == "__main__":
    TestConfig.use_cli()
    cfg = TestConfig()
    print(cfg)
