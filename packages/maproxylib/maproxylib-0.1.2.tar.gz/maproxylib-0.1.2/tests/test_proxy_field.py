from dataclasses import dataclass, field

from maproxylib import ProxyField, ProxyFieldFactory

params_field = ProxyFieldFactory(storage_name="params")


@dataclass
class MyModel:
    params: dict = field(default_factory=dict)
    name = ProxyField[str](storage_name="params", default="Guest")
    name2 = ProxyField[str](storage_name="params", default="Guest2", path=["group"])
    age = params_field(key="age", default=30)


def test_default_values():
    obj = MyModel()
    assert obj.name == "Guest"
    assert obj.age == 30


def test_no_default_storage_values():
    obj = MyModel()
    assert obj.params == {}


def test_set_direct_and_get_values():
    obj = MyModel()
    obj.name = "Alice"
    obj.age = 25

    assert obj.name == "Alice"
    assert obj.age == 25
    assert obj.params["name"] == "Alice"
    assert obj.params["age"] == 25


def test_set_init_and_get_values():
    obj = MyModel(params=dict(name="Alice", age=25))

    assert obj.params["name"] == "Alice"
    assert obj.params["age"] == 25


def test_multiple_instances_do_not_share_state():
    obj1 = MyModel()
    obj2 = MyModel()

    obj1.name = "Bob"
    obj2.name = "Alice"

    assert obj1.name == "Bob"
    assert obj2.name == "Alice"
