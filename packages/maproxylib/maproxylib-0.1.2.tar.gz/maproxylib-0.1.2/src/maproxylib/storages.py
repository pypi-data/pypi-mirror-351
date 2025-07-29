"""
This module implements a Storage abstraction for working with nested data structures.
Currently supports dictionary-like and object-based storages.
Support for other types (e.g. Pydantic models) can be added in the future.

Example:
>>> my_storage = Storage(
    {
        "a": 1,
        "b": {
            "c": 3,
            "d": {
                "e": 5,
            },
        },
    },
    read_only=True,
)
>>> my_storage.get("a")
1
>>> my_storage.get("b")
{'c': 3, 'd': {'e': 5}}
>>> my_storage.get_nested_value(["b", "d"], key="e")
5
>>> my_storage.get_nested_storage(["b", "d"]).data
{'e': 5}
>>> my_storage.get_nested_storage(["b", "d"]).get("e")
5
"""

from abc import abstractmethod
from typing import Any, Callable, Generic, TypeVar, get_args

T = TypeVar("T")

storage_registry = {}


class BaseStorage(Generic[T]):
    """
    Abstract base class for all storage types.
    Implements common logic for working with nested paths and read-only mode.
    """

    def __init__(self, data: T, read_only: bool = False):
        self.data: T = data
        self.read_only = read_only

    def get_nested_storage(self, path: list[str] | None = None):
        """
        Returns a nested storage by the given path.
        If part of the path is missing, creates it (unless in read-only mode).
        """
        path = path or []
        target_storage = self
        for step in path:
            target_storage = Storage(
                data=target_storage.get(key=step, default_factory=dict),
                read_only=self.read_only,
            )
        return target_storage

    def get_nested_value(
        self,
        path: list[str],
        key: str,
        default_factory: Callable | None = None,
    ) -> Any:  # noqa: ANN401
        """
        Retrieves a value from a nested storage using the given path and key.
        """
        return self.get_nested_storage(path).get(key, default_factory)

    def set_nested_value(
        self,
        path: list[str],
        key: str,
        value: Any,  # noqa: ANN401
    ) -> None:
        """
        Sets a value in a nested storage at the specified path and key.
        """
        if self.read_only:
            raise ValueError("Storage is read-only")
        self.get_nested_storage(path).set(key, value)

    @abstractmethod
    def get(self, key: str, default_factory: Callable | None = None) -> Any:  # noqa: ANN401
        """
        Gets a value by key. May use a factory to generate a default value.
        """

    @abstractmethod
    def set(self, key: str, value: Any):  # noqa: ANN401
        """
        Sets a value by key.
        """

    def __getitem__(self, key: str) -> Any:  # noqa: ANN401
        return self.get(key)

    def __setitem__(self, key: str, value: Any):  # noqa: ANN401
        self.set(key, value)

    def __init_subclass__(cls, **kwargs):  # noqa: ANN003
        """
        Automatically registers the class as a handler for a specific data type.
        Uses `__orig_bases__` to extract the TypeVar parameter.
        """
        super().__init_subclass__(**kwargs)

        orig_bases = getattr(cls, "__orig_bases__", ())

        for base in orig_bases:
            origin = getattr(base, "__origin__", None)
            if origin is not BaseStorage:
                continue

            args = get_args(base)
            if len(args) != 1:
                continue

            storage_type = args[0]
            storage_registry[storage_type] = cls
            break


class DictStorage(BaseStorage[dict]):
    """
    Storage implementation that works with dict-type data.
    """

    def get(self, key: str, default_factory: Callable | None = None) -> Any:  # noqa: ANN401
        """
        Returns a value from the dictionary. If the key is missing:
        - in read-only mode: returns the result of default_factory or None;
        - otherwise: creates the key with the default value if a factory is provided.
        """
        if key in self.data:
            return self.data[key]
        if self.read_only:
            if default_factory is None:
                return None
            return default_factory()
        # Only in mutable mode
        if default_factory is not None:
            self.data[key] = default_factory()
        return self.data[key]

    def set(self, key: str, value: Any):  # noqa: ANN401
        """
        Sets a value in the dictionary.
        """
        if self.read_only:
            raise ValueError("Storage is read-only")
        self.data[key] = value


class ObjectStorage(BaseStorage[object]):
    """
    Storage implementation that works with Python objects.
    Requires attributes to exist at the time of access.
    """

    def get(self, key: str, default_factory: Callable | None = None) -> Any:  # noqa: ANN401
        """
        Returns an object attribute. Raises AttributeError if the attribute does not exist.
        TODO: Should we allow dynamic creation of attributes?
        """
        if not hasattr(self.data, key):
            raise AttributeError(f"Object has no attribute {key}")
        return getattr(self.data, key)

    def set(self, key: str, value: Any):  # noqa: ANN401
        """
        Sets an object attribute.
        """
        if self.read_only:
            raise ValueError("Storage is read-only")
        if not hasattr(self.data, key):
            raise AttributeError(f"Object has no attribute {key}")
        setattr(self.data, key, value)


class Storage:
    """
    Factory that returns the appropriate storage type for the given data.
    """

    def __new__(cls, data: T, read_only: bool = False) -> BaseStorage[T]:
        for data_type, storage_class in storage_registry.items():
            if isinstance(data, data_type):
                return storage_class(data, read_only)
        raise TypeError(f"No storage registered for {type(data)}")
