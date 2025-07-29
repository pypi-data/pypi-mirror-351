from dataclasses import dataclass, field

import pytest

from maproxylib import ProxyField, ProxyFieldFactory

params_ro_field = ProxyFieldFactory(storage_name="params", read_only=True)


@dataclass
class Params:
    name: str = "ObjectGuest"
    age: int = 33
    skills: dict = field(default_factory=dict)


@dataclass
class MyModel:
    params: Params = field(default_factory=Params)
    name = ProxyField[str](storage_name="params", default="Guest")
    age = params_ro_field(key="age", default=30)
    skill_1 = params_ro_field[int](path="skills.lang", key="Python", default=10)


def test_inner_dict_ro_storage():
    obj = MyModel()
    assert obj.params.skills == {}
    assert obj.skill_1 == 10
    assert obj.params.skills == {}
    with pytest.raises(ValueError):
        obj.skill_1 = 20
    assert obj.skill_1 == 10
    assert obj.params.skills == {}
    assert obj.skill_1 == 10
    obj.params.skills["lang"] = {"Python": 20}
    assert obj.params.skills["lang"]["Python"] == 20
    assert obj.skill_1 == 20
    del obj.params.skills["lang"]["Python"]
    assert obj.skill_1 == 10
    assert obj.params.skills == {"lang": {}}
    del obj.params.skills["lang"]
    assert obj.skill_1 == 10
    assert obj.params.skills == {}
    with pytest.raises(AttributeError):
        del obj.skill_1
