from datetime import date

from sanic_openapi.spec import Spec


def test_build_definition_with_containing_class():
    spec = Spec(config={})

    class Manufacturer:
        name: str
        start_date: date

    class Car:
        on: bool
        doors: int
        color: str
        make: Manufacturer

    spec._build_definition(definition=Car)

    assert len(spec.definitions) == 2


def test_build_definition_with_list_of_class():
    spec = Spec(config={})

    class Manufacturer:
        name: str
        start_date: date

    class Car:
        on: bool
        doors: int
        color: str
        makers: [Manufacturer]

    spec._build_definition(definition=Car)

    assert len(spec.definitions) == 2
