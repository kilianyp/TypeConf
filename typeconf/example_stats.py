from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class TrackedModel(BaseModel):
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


class Tester(TrackedModel):
    name : str = "test"
    name2 : str = "test2"


class User(TrackedModel):
    id: int
    name = 'John Doe'
    signup_ts: Optional[datetime] = None
    friends: List[int] = []
    tester : Tester


external_data = {
    'id': '123',
    'signup_ts': '2019-06-01 12:22',
    'friends': [1, 2, '3'],
    'tester': {}
}
user = User(**external_data)

print(user.get_stats())  # {}
user.id
print(user.get_stats())  # {'id': 1}
user.id
print(user.get_stats())  # {'id': 2}
print(user)
print(user.get_stats())  # {'id': 3}
user.tester
print(user.get_stats())
user.tester.name
print(user.get_stats())
print(user.tester.get_stats())
print(user.find_unused())
