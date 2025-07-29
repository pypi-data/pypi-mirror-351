from dataclasses import dataclass, field

from maproxylib import ProxyField, ProxyFieldFactory

params_field = ProxyFieldFactory(storage_name="params")


@dataclass
class Params:
    name: str = "ObjectGuest"
    age: int = 33
    skills: dict = field(default_factory=dict)


@dataclass
class MyModel:
    params: Params = field(default_factory=Params)
    name = ProxyField[str](storage_name="params", default="Guest")
    age = params_field(key="age", default=30)
    skill_1 = params_field[int](path=["skills", "lang"], key="Python", default=10)


def test_default_values():
    obj = MyModel()
    assert obj.name == "ObjectGuest"
    assert obj.age == 33


def test_no_default_storage_values():
    obj = MyModel()
    assert obj.params == Params(name="ObjectGuest", age=33)


def test_set_direct_and_get_values():
    obj = MyModel()
    obj.name = "Alice"
    obj.age = 25

    assert obj.name == "Alice"
    assert obj.age == 25
    assert obj.params.name == "Alice"
    assert obj.params.age == 25


def test_set_init_and_get_values():
    obj = MyModel(params=Params(name="Alice", age=25))

    assert obj.name == "Alice"
    assert obj.age == 25
    assert obj.params.name == "Alice"
    assert obj.params.age == 25


def test_multiple_instances_do_not_share_state():
    obj1 = MyModel()
    obj2 = MyModel()

    obj1.name = "Bob"
    obj2.name = "Alice"

    assert obj1.name == "Bob"
    assert obj2.name == "Alice"


def test_inner_dict_storage():
    obj = MyModel()
    assert obj.params.skills == {}
    assert obj.skill_1 == 10
    assert obj.params.skills == {"lang": {"Python": 10}}
    obj.params.skills["lang"]["Python"] = 20
    assert obj.skill_1 == 20
    obj.skill_1 = 30
    assert obj.params.skills == {"lang": {"Python": 30}}
    obj.skill_1 = None
    assert obj.params.skills == {"lang": {"Python": None}}
