"""
Reads Command Line input

Is configured from pydantic object
for flag
for list
for single value

no type checking
no default value
Can we make this nested without adding all to one parser with . separation?
Meaning every config adds to the parser

Syntactic sugar with presets?

Print help also in a nested fashion
"""
import inspect
from typeconf import BaseConfig, SelectConfig
import sys as _sys
import functools


def isxtype(cls, x):
    from typing import Union

    d = getattr(cls, '__dict__', None)
    if d is None:
        return False
    origin = d.get('__origin__')
    if origin == x:
        return True
    if origin == Union:
        args = d.get('__args__')
        if args is None:
            return False
        for a in args:
            if isxtype(a, x):
                return True
    return False


islisttype = functools.partial(isxtype, x=list)
istupletype = functools.partial(isxtype, x=tuple)


class Action(object):
    def __init__(self,
                 dest):
        self.dest = dest

    def __call__(self):
        raise NotImplemented


class DefaultAction(Action):
    def __call__(self, value):
        return value[0]


class ListAction(Action):
    def __call__(self, value):
        return value


class Parser(object):
    def __init__(self,
                 prefix_chars='-'):
        self.prefix_chars = prefix_chars
        self._actions = {}
        self._subparsers = {}

    def add_argument(self, dest, type='default', **kwargs):
        if not dest.startswith('--'):
            raise ValueError("Only -- arguments supported")
        action_name = dest[2:]

        if action_name in self._actions:
            raise ValueError(f'destination {action_name} exists')

        if type == 'default':
            self._actions[action_name] = DefaultAction(action_name)
        elif type == 'list':
            self._actions[action_name] = ListAction(action_name)
        else:
            raise ValueError(f'Unknown type {type}')

    def add_subparser(self, parser, name):
        self._subparsers[name] = parser
        return parser

    def parse_args(self, args=None):
        """
        args: List
        """
        if args is None:
            args = _sys.argv[1:]
        else:
            args = list(args)

        args = Parser.arglist2dict(args)
        return self._parse_args(args)

    def _parse_args(self, args : dict):
        result = {}
        for key, value in args.items():
            if key in self._subparsers:
                result[key] = self._subparsers[key]._parse_args(value)
            elif key in self._actions:
                result[key] = self._actions[key](value)
            else:
                raise ValueError("Unknown argument")

        return result


    @staticmethod
    def arglist2dict(args):
        arg_dict = {}

        if len(args) == 0:
            return arg_dict

        if not args[0].startswith('--'):
            raise ValueError(f"Positional keywords are not supported: {args[0]}")

        i = 0
        while i < len(args):
            arg = args[i]
            i = i + 1
            if arg.startswith('--'):
                dest = arg[2:]
                j, arglist = Parser.get_args(args[i:])
                i = i + j
                Parser.update_arg_dict(arg_dict, dest, arglist)
        return arg_dict

    @staticmethod
    def update_arg_dict(argdict, keystring, value):
        keys = keystring.split('.')
        updatedict = argdict
        for key in keys[:-1]:
            if key in updatedict:
                updatedict = updatedict[key]
                if not isinstance(updatedict, dict):
                    raise ValueError("Will overwrite a value")
            else:
                updatedict[key] = {}
                updatedict = updatedict[key]

        updatedict[keys[-1]] = value

    @staticmethod
    def get_args(args):
        arglist = []
        for idx, arg in enumerate(args):
            if arg.startswith('-'):
                break
            arglist.append(arg)

        if len(arglist) == 0:
            raise ValueError("Flag is not allowed")
        return idx, arglist

    @staticmethod
    def from_config(config):
        """
        Avoids any parsing functionality --> all optional

        args:
            config: Pydantic model
        """

        if issubclass(config, SelectConfig):
            parser = DynamicParser()
        else:
            parser = Parser()

        for key, f in config.__fields__.items():
            if inspect.isclass(f.outer_type_) and issubclass(f.outer_type_, BaseConfig):
                subparser = Parser.from_config(f.outer_type_)
                parser.add_subparser(subparser, key)
            else:
                if islisttype(f.outer_type_) or istupletype(f.outer_type_):
                    type = "list"
                else:
                    type = "default"
                parser.add_argument(f"--{f.name}", type=type)
        return parser


class DynamicParser(Parser):
    def _parse_args(self, args):
        """
        args: dict
        """
        # current behviour for unknown. If list with 1 value return 1 value
        for key, values in args.items():
            if isinstance(values, list) and len(values) == 1:
                args[key] = values[0]
        return args
