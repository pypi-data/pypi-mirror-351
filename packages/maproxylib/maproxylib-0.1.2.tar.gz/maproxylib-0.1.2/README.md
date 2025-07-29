# 🗝️ maproxylib — Mapping Proxy Library

> Transparent access to nested objects/dicts fields via descriptors.

🇷🇺 [Читать на русском](README.ru.md)

`maproxylib` is a lightweight Python library that allows you to **transparently access inner objects/dicts fields as class attributes**, using the power of **descriptors**. Especially useful when working with JSON models, DTOs, complex nested structures, and API responses.

[![PyPI version](https://img.shields.io/pypi/v/maproxylib)](https://pypi.org/project/maproxylib/)
[![Python versions](https://img.shields.io/pypi/pyversions/maproxylib)](https://pypi.org/project/maproxylib/)
[![License: MIT](https://img.shields.io/github/license/arnetkachev/maproxylib)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/arnetkachev/maproxylib/actions/workflows/publish.yml/badge.svg)](https://github.com/arnetkachev/maproxylib/actions)

---

## ✨ Features

- Simple dot-style access to dictionary values  
- Support for deeply nested structures (via `path`)  
- Type hint support (`typing`, `TypeVar`)  
- Integration with `dataclasses`  
- Read-only fields support

---

## 🚀 Installation
Various dependency management tools are supported:

### pip
```bash
pip install maproxylib
```

### poetry
```bash
poetry add maproxylib
```

### uv
```bash
uv add maproxylib
```

---

## 💡 Usage Examples

### 1. Basic Usage

```python
from dataclasses import dataclass, field

from maproxylib import ProxyFieldFactory

params_field = ProxyFieldFactory(storage_name="params")
# Descriptor factory for storage `params`

@dataclass
class MyModel:
    params: dict = field(default_factory=dict)
    # The storage for `params_field` descriptors

    name = params_field[str](default="Guest")
    age = params_field[int](default=30)

model = MyModel()
assert model.name == "Guest"  # Default value (storage is empty)

model.name = "Alice"  # Set values in storage
model.age = 25
assert model.params == {"name": "Alice", "age": 25}  # Actual values in storage
```

### 2. Nested Fields

```python
from dataclasses import dataclass, field

from maproxylib import ProxyFieldFactory

data_field = ProxyFieldFactory(storage_name="data")
# Descriptor fabric for storage `data`

@dataclass
class User:
    data: dict = field(default_factory=dict)  # Storage
    city = data_field[str](key="address.city", default="Unknown")
    # The descriptor key in dot notation represents access to `data["address"]["city"]`

user = User()
user.city = "Moscow"  # Same as user.data["address"]["city"] = "Moscow"

assert user.data == {"address": {"city": "Moscow"}}
# The storage contains current values ​​in the required structure
```

---

## 📦 Key Components

| Component | Description |
|----------|-------------|
| `ProxyField[T]` | A descriptor that provides access to a field |
| `ProxyFieldFactory(...)` | Factory for creating descriptors with preset parameters |

---

## 🧪 Testing

You can easily test with `pytest`:

```bash
uv sync --group dev
uv run pytest
```

---

## 🛠️ Development

To install the package locally in development mode:

```bash
uv sync --group dev
uv install -e .
```

---

## 🤝 Contributing

Any suggestions, feature requests, and PRs are welcome!  
Feel free to open issues on GitHub 👉 [issues](https://github.com/yourname/maproxylib/issues)

---

## ⚖️ License

MIT License – see the [`LICENSE`](LICENSE) file for details.

---

## 📬 Author

- [@arnetkachev](https://github.com/arnetkachev)

---

## 🔗 Links

- PyPI: https://pypi.org/project/maproxylib/
- GitHub: https://github.com/arnetkachev/maproxylib
