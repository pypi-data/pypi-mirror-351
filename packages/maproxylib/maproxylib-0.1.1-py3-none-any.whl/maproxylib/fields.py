"""
This module provides a descriptor-based interface
for accessing nested data structures via ProxyField.

Allows transparent access to values stored in hierarchical storages (like dicts or objects),
presenting them as regular class attributes.

Example:
>>> params_field = ProxyFieldFactory(storage_name="params")
>>>
>>> @dataclass
>>> class MyModel:
>>>     params: dict = field(default_factory=dict)
>>>     name = ProxyField[str](storage_name="params", default="Guest")
>>>     age = params_field(key="age", default=30)
>>>
>>> obj = MyModel()
>>> obj.name = "Alice"
>>> obj.age = 25
>>>
>>> assert obj.name == "Alice"
>>> assert obj.age == 25
>>> assert obj.params["name"] == "Alice"
>>> assert obj.params["age"] == 25
"""

from typing import Any, Callable, Generic, Optional, TypeVar, cast

from maproxylib.storages import BaseStorage

from .storages import Storage  # Assuming this is your own storage implementation

T = TypeVar("T", type, Any)


def _simple_return_value(value: Any) -> Any:  # noqa: ANN401
    """Default value converter that simply returns the input."""
    return value


def _normalize_path(
    key: str | None = None,
    path: str | list[str] | None = None,
) -> tuple[str | None, list[str]]:
    """
    Converts dot-separated strings into path lists and merges with provided path.

    Example:
        key="a.b.c", path=["x", "y"] => ("c", ["x", "y", "a", "b"])

    This function helps construct paths through nested dictionaries or object attributes.
    """
    key_path: list[str] = []
    match key:
        case None:
            key_path, key = [], None
        case str():
            *key_path, key = key.split(".")
    match path:
        case None:
            path = key_path
        case str():
            path = path.split(".") + key_path
        case list():
            path += key_path
        case _:
            raise TypeError(f"Unknown path type: {path=}")
    return key, path


class ProxyField(Generic[T]):
    """
    Descriptor class that allows transparent access to nested fields in a storage.

    Attributes:
        storage_name: Name of the attribute holding the storage object.
        default: Default value if no value exists at the path/key.
        key: Key within the final level of the path.
        path: Path to navigate through nested storages.
        read_only: If True, prevents assignment.
        data_type: Expected type of the value.
        custom_type_converter: Optional function to convert value to expected type.
    """

    data_type: Optional[T] = None
    storage_name: str | None = None
    path: list[str] | None = None
    read_only: bool = False

    def __init__(
        self,
        storage_name: Optional[str] = None,
        default: Optional[T] = None,
        key: Optional[str] = None,
        path: Optional[str | list[str]] = None,
        read_only: bool = False,
        data_type: Optional[T] = None,
        custom_type_converter: Optional[Callable[..., T]] = None,
    ):
        """
        Initializes a new ProxyField instance.

        Args:
            storage_name: Attribute name where the storage lives in the parent class.
            default: Value used when none is found at the given path/key.
            key: Final key in the path where the value is stored.
            path: Nested path leading to the final key.
            read_only: Prevents assignment if True.
            data_type: Expected type of the value.
            custom_type_converter: Optional function to convert raw value to desired type.

        Note: Avoid specifying both `data_type` in annotation and constructor.
        """
        self.storage_name = storage_name or type(self).storage_name
        if self.storage_name is None:
            raise AttributeError("You must specify the storage_name for the field.")
        self.default = default
        self.key, self.path = _normalize_path(key, path or type(self).path)
        self.read_only = read_only or type(self).read_only

        if type(self).data_type is not None and data_type is not None:
            raise AttributeError(
                "It is forbidden to specify data_type "
                "for an annotation and for as an argument at the same time."
            )
        self.data_type = data_type or type(self).data_type
        self.type_converter: Callable[..., T] = _simple_return_value
        if custom_type_converter is not None:
            self.type_converter = custom_type_converter
        elif all([
            self.data_type is not None,
            self.data_type is not Any,
            callable(self.data_type),
        ]):
            self.type_converter = cast(Callable[..., T], self.data_type)

    def __set_name__(self, owner: type, name: str):
        """
        Automatically assigns the field name as the key if not explicitly set.
        Useful when you want to avoid duplicating field names manually.
        """
        if not self.key:
            self.key = name

    def __get__(self, instance: object, owner: type) -> T | None:
        """
        Gets the value from the nested storage by path and key.
        Applies type conversion if necessary.
        """
        if instance is None:
            return None
        storage = self.get_storage(instance)
        value = storage.get_nested_value(
            path=self.path or [], key=self.key or "<UNKNOWN>", default_factory=lambda: self.default
        )
        return self._check_convert_type(value or self.default)

    def __set__(self, instance: object, value: T):
        """
        Sets the value in the nested storage by path and key.
        """
        if instance is None:
            return
        storage = self.get_storage(instance)
        storage.set_nested_value(path=self.path or [], key=self.key or "<UNKNOWN>", value=value)

    def _check_convert_type(self, value: Any) -> T:  # noqa: ANN401
        """
        Ensures the value matches the expected type using either:
        - a custom converter
        - a type constructor
        - simple pass-through

        TODO: Should we allow implicit conversion even when it's lossy?
        """
        if self._is_type_correct(value):
            return value
        return self.type_converter(value)

    def _is_type_correct(self, value: Any) -> bool:  # noqa: ANN401
        """
        Checks if the value is already of the correct type.
        """
        return self.data_type in (None, Any) or isinstance(value, self.data_type)

    def get_storage(self, instance: object) -> BaseStorage:
        """
        Retrieves the storage associated with this field.
        Raises error if storage doesn't exist on the instance.
        """
        if self.storage_name is None:
            raise AttributeError("You must specify the storage_name for the field.")
        if not hasattr(instance, self.storage_name):
            raise AttributeError(f"Unknown storage name in {instance}.{self.storage_name}")
        return Storage(getattr(instance, self.storage_name), read_only=self.read_only)

    @classmethod
    def __class_getitem__(cls, item: T) -> type["ProxyField[T]"]:
        """
        Allows syntax like ProxyField[int] to create typed proxy fields.
        """

        class TypedProxyField(cls):
            data_type = item

        return TypedProxyField


class ProxyFieldFactory:
    """
    Factory for creating ProxyField instances with shared configuration.
    Useful for reusing common settings like storage_name and path.
    """

    def __init__(
        self,
        storage_name: str,
        path: Optional[str | list[str]] = None,
        read_only: bool = False,
    ):
        self.storage_name = storage_name
        _, self.path = _normalize_path(path=path)
        self.read_only = read_only

    def __getitem__(self, item: T) -> type[ProxyField[T]]:
        """
        Creates a typed ProxyField class with predefined storage and path.
        """

        class TypedProxyField(ProxyField[item]):
            storage_name = self.storage_name
            data_type = item
            path = self.path
            read_only = self.read_only

        return TypedProxyField

    def __call__(  # TODO replace attribs with kwargs: Unpack(TypedDict)
        self,
        default: T | None = None,
        key: Optional[str] = None,
        path: Optional[str | list[str]] = None,
        read_only: bool = False,
        data_type: T | None = None,
        custom_type_converter: Optional[Callable] = None,
    ) -> ProxyField:
        """
        Creates a new ProxyField instance with optional overrides.
        """
        key, path = _normalize_path(key=key, path=path)
        return self.__getitem__(Any)(
            storage_name=self.storage_name,
            default=default,
            key=key,
            path=path,
            read_only=read_only,
            data_type=data_type,
            custom_type_converter=custom_type_converter,
        )
