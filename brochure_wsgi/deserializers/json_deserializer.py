from json import loads
from typing import Generic, TypeVar, Callable

T = TypeVar('T')
U = TypeVar('U')


class JSONDeserializer(Generic[T, U]):
    def __init__(self, deserializer: Callable[[T], U]):
        self._deserializer = deserializer
        super().__init__()

    def __call__(self, json: str, *args, **kwargs) -> U:
        deserialized_json = loads(json)
        if self._deserializer is not None:  # pragma nocover
            return self._deserializer(deserialized_json)

        return deserialized_json  # pragma nocover
