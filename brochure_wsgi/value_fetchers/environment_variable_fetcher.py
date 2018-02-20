import os
from typing import Callable, Generic, TypeVar

T = TypeVar('T')


class EnvironmentVariableFetcher(Generic[T]):

    def __init__(self, key: str, deserializer: Callable[[str], T]) -> None:
        self._key = key
        self._deserializer = deserializer
        super().__init__()

    def __call__(self, *args, **kwargs) -> T:
        string_value = os.environ.get(self._key)

        return self._deserializer(string_value)
