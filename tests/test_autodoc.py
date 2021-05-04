from sanic_openapi import autodoc

tests = []

_ = ""

tests.append({"doc": _, "expects": {}})

_ = "one line docstring"

tests.append({"doc": _, "expects": {"summary": "one line docstring"}})

_ = """
first line

more lines
"""

tests.append(
    {"doc": _, "expects": {"summary": "first line", "description": "more lines"}}
)


_ = """
first line

more lines

openapi:
---
responses:
  '200':
    description: OK
"""

tests.append(
    {
        "doc": _,
        "expects": {
            "summary": "first line",
            "description": "more lines",
            "responses": {"200": {"description": "OK"}},
        },
    }
)


def test_autodoc():
    for t in tests:
        parser = autodoc.YamlStyleParametersParser(t["doc"])
        assert parser.to_openAPI_2() == t["expects"]
        assert parser.to_openAPI_3() == t["expects"]
