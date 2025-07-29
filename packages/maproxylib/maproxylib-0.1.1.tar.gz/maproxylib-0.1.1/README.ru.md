# 🗝️ maproxylib — Mapping Proxy Library

> Прозрачный доступ к полям вложенных объектов через дескрипторы.

🇬🇧 [Read in English](README.md)

`maproxylib` — это легковесная Python-библиотека, которая позволяет **прозрачно обращаться к полям вложенных словарей и объектов как к атрибутам родительского класса**, используя механизмы **дескрипторов**. Особенно удобна при работе с JSON-моделями, DTO, сложными вложенными структурами и API-ответами.

[![PyPI version](https://img.shields.io/pypi/v/maproxylib)](https://pypi.org/project/maproxylib/)
[![Python versions](https://img.shields.io/pypi/pyversions/maproxylib)](https://pypi.org/project/maproxylib/)
[![License: MIT](https://img.shields.io/github/license/arnetkachev/maproxylib)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/arnetkachev/maproxylib/actions/workflows/publish.yml/badge.svg)](https://github.com/arnetkachev/maproxylib/actions)

---

## ✨ Возможности

- Простой доступ к значениям словаря или вложенного объекта через точечную нотацию
- Работа с вложенными структурами на любую глубину (через `path`)
- Поддержка аннотаций типов (`typing`, `TypeVar`)
- Интеграция с `dataclasses`
- Поддержка read-only-полей

---

## 🚀 Установка
Поддерживаются разные инструменты управления зависимостями:

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

## 💡 Примеры использования

### 1. Базовое использование

```python
from dataclasses import dataclass, field

from maproxylib import ProxyFieldFactory

params_field = ProxyFieldFactory(storage_name="params")
# Фабрика дескрипторов для хранилища `params`

@dataclass
class MyModel:
    params: dict = field(default_factory=dict)
    # Хранилище, доступное для дескрипторов `params_field`

    name = params_field[str](default="Guest") # Дескрипторы
    age = params_field[int](default=30)

model = MyModel()
assert model.name == "Guest"  # Значение по умолчанию (хранилище пустое)

model.name = "Alice"  # Установка значений через дескрипторы
model.age = 25
assert model.params == {"name": "Alice", "age": 25}  # Актуальные значения в хранилище
```

### 2. Вложенные поля

```python
from dataclasses import dataclass, field

from maproxylib import ProxyFieldFactory

data_field = ProxyFieldFactory(storage_name="data")
# Фабрика дескрипторов для хранилища `data`

@dataclass
class User:
    data: dict = field(default_factory=dict)  # Storage
    city = data_field[str](key="address.city", default="Unknown")
    # Ключ дескриптора в точечной нотации представляет доступ к `data["address"]["city"]`

user = User()
user.city = "Moscow"  # Аналогично: user.data["address"]["city"] = "Moscow"

assert user.data == {"address": {"city": "Moscow"}}
# В хранилище актуальные значения в нужной структуре
```

---

## 📦 Ключевые компоненты

| Компонент | Описание |
|----------|----------|
| `ProxyField[T]` | Дескриптор, предоставляющий доступ к полю |
| `ProxyFieldFactory(...)` | Фабрика для создания дескрипторов с предустановленными параметрами |

---

## 🧪 Тестирование

Можно легко тестировать с помощью `pytest`:

```bash
uv sync --group dev
uv run pytest
```

---

## 🛠️ Разработка

Для разработки установи локально в режиме редактирования:

```bash
uv sync --group dev
uv install -e .
```

---

## 🤝 Участие в проекте

Любые предложения, фич-реквесты и PR'ы приветствуются!  
Смело открывайте issues на GitHub 👉 [issues](https://github.com/arnetkachev/maproxylib/issues)

---

## ⚖️ Лицензия

MIT License – см. файл [`LICENSE`](LICENSE) для подробностей.

---

## 📬 Автор

- [@arnetkachev](https://github.com/arnetkachev)

---

## 🔗 Ссылки

- PyPI: https://pypi.org/project/maproxylib/
- GitHub: https://github.com/arnetkachev/maproxylib
