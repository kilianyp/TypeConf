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
from typeconf import BaseConfig
import sys as _sys


def islisttype(cls):
    from typing import Union

    d = getattr(cls, '__dict__', None)
    if d is None:
        return False
    origin = d.get('__origin__')
    if origin == list:
        return True
    if origin == Union:
        args = d.get('__args__')
        if args is None:
            return False
        for a in args:
            if islisttype(a):
                return True
    return False


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

    def add_argument(self, dest, type='default', **kwargs):
        if not dest.startswith('--'):
            raise ValueError("Arguments must start with --")

        action_name = dest[2:]

        if action_name in self._actions:
            raise ValueError(f'destination {action_name} exists')

        if type == 'default':
            self._actions[action_name] = DefaultAction(action_name)
        elif type == 'list':
            self._actions[action_name] = ListAction(action_name)
        else:
            raise ValueError(f'Unknown type {type}')

    def parse_args(self, args=None, namespace=None):
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
                actions_arg = []
                actions_args.append(actions_arg)
            else:
                if actions_arg is None:
                    raise ValueError(f"Positional keywords are not supported: {actions_arg}")
                actions_arg.append(arg)

        result = {}
        for action_name, action_arg in zip(actions, actions_args):
            if action_name not in self._actions:
                raise ValueError(f"Unknown parameter {action_name}")
            action = self._actions[action_name]
            result[action.dest] = action(action_arg)

        return nested2dict(result)


    def add_subparser(self, name):
        pass


    @staticmethod
    def from_config(config):
        parser = Parser()
        fields2args(parser, config.__fields__)
        return parser


def fields2args(parser, fields, prefix=''):
    """
    Avoids any parsing functionality --> all optional

    args:
        fields: Pydantic fields
        parser: ArgumentParser
    """
    for key, f in fields.items():
        if inspect.isclass(f.outer_type_) and issubclass(f.outer_type_, BaseConfig):
            fields2args(
                parser,
                f.outer_type_.__fields__,
                prefix + f.name + '.')
            # TODO this is necessary because otherwise
            # when instantiating the sub config it will complain
            # AttributeError: _parser
            # ALternative would be that each class parses it's own arguments
            f.outer_type_._parser = None
        else:
            if islisttype(f.outer_type_):
                type = "list"
            else:
                type = "default"
            parser.add_argument(f'--{prefix}{f.name}', type=type)

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
