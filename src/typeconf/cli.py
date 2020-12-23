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

    def parse_args(self, args=None, namespace=None):
        """
        args: List
        """
        if args is None:
            args = _sys.argv[1:]
        else:
            args = list(args)

        actions = []
        actions_args = []
        actions_arg = None
        for i, arg in enumerate(args):
            if arg.startswith('--'):
                action_name = arg[2:]
                actions.append(action_name)
                if actions_arg is not None and len(actions_arg) == 0:
                    raise ValueError()
                actions_arg = []
                actions_args.append(actions_arg)
            else:
                if actions_arg is None:
                    raise ValueError(f"Positional keywords are not supported: {actions_arg}")
                actions_arg.append(arg)

        if len(args) > 0 and len(actions_arg) == 0:
            raise ValueError()

        result = {}
        for action_name, action_arg in zip(actions, actions_args):
            split = action_name.split('.')
            if len(split) == 1:
                if action_name not in self._actions:
                    raise ValueError(f"Unknown parameter {action_name}")
                action = self._actions[action_name]
                result[action.dest] = action(action_arg)
            else:
                subparser = self._subparsers[split[0]]
                subresult = subparser.parse_args(["--" + '.'.join(split[1:])] + action_arg)
                if split[0] in result:
                    result[split[0]].update(subresult)
                else:
                    result[split[0]] = subresult

        return result

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


def nested2dict(dic):
    """
    Converts a dict with keys such as KEY1.KEY2 = VALUE
    Into a nested dict
    Filters out unset values
    """
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

class DynamicParser(Parser):
    def parse_args(self, args=None, namespace=None):
        """
        args: List
        """
        if args is None:
            args = _sys.argv[1:]
        else:
            args = list(args)

        result = {}
        action_name = None
        for i, arg in enumerate(args):
            if arg.startswith('--'):
                action_name = arg[2:]
                action_args = []
                result[action_name] = action_args
            else:
                if action_name is None:
                    raise RuntimeError()
                action_args.append(arg)
        # if there's only one arg, return scalar
        for key, values in result.items():
            if len(values) == 1:
                result[key] = values[0]

        return result
