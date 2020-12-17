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

Print help also in a nested fashion
"""
import sys as _sys


class Action(object):
    def __init__(self,
                 dest):
        self.dest = dest

    def __call__(self):
        raise NotImplemented


class DefaultAction(Action):
    def __call__(self, value):
        return value[0]


class Parser(object):
    def __init__(self,
                 prefix_chars='-'):
        self.prefix_chars = prefix_chars
        self._actions = {}

    def add_argument(self, dest, **kwargs):
        action_name = dest[2:]
        self._actions[action_name] = DefaultAction(action_name)

    def parse_args(self, args=None, namespace=None):
        if args is None:
            args = _sys.argv[1:]
        else:
            args = list(args)

        actions = []
        actions_args = []
        for i, arg in enumerate(args):
            if arg.startswith('--'):
                action_name = arg[2:]
                actions.append(action_name)
                actions_arg = []
                actions_args.append(actions_arg)
            else:
                actions_arg.append(arg)

        result = {}
        for action_name, action_arg in zip(actions, actions_args):
            action = self._actions[action_name]
            result[action.dest] = action(action_arg)
        return result
