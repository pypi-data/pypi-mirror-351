def test_readme_example1():
    from dataclasses import dataclass, field

    from maproxylib import ProxyFieldFactory

    params_field = ProxyFieldFactory(storage_name="params")
    # Descriptor fabric for storage `params`

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
    assert model.params == {"name": "Alice", "age": 25}  # Values in storage


def test_readme_example2():
    from dataclasses import dataclass, field

    from maproxylib import ProxyFieldFactory

    data_field = ProxyFieldFactory(storage_name="data")
    # Descriptor factory for storage `data`

    @dataclass
    class User:
        data: dict = field(default_factory=dict)  # Storage
        city = data_field[str](key="address.city", default="Unknown")
        # The descriptor key in dot notation represents access to `data["address"]["city"]`

    user = User()
    user.city = "Moscow"  # Same as user.data["address"]["city"] = "Moscow"

    assert user.data == {"address": {"city": "Moscow"}}
    # The storage contains current values ​​in the required structure
