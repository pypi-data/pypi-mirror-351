from typing import Any


def _simple_return_value(value: Any) -> Any:  # noqa: ANN401
    """Default value converter that simply returns the input."""
    return value


def _normalize_path(
    key: str | None = None,
    path: str | list[str] | None = None,
    sep: str = ".",
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
            *key_path, key = key.split(sep)
        case _:
            raise TypeError(f"Unknown key type: {key=}")
    match path:
        case None:
            path = key_path
        case str():
            path = path.split(sep) + key_path
        case list():
            path += key_path
        case _:
            raise TypeError(f"Unknown path type: {path=}")
    return key, path
