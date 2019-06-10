# Contributing Guide

First of all, thank you for joining us to make this project better. Here are some guidelines to help you contribute to this project. We hope that you find them useful.

## Develop Installation

Before starting your development, you can set up your development environment by the following command:

```shell
pip install -e .['dev']
```

This development setup will install following modules:

* black
* coverage
* flake8
* isort
* pytest
* tox

## Run Tests

If you want to run all tests without install `dev` requirements, you can install `test` requirements by:

```shell
pip install -e .['test']
```

To run tests, use `test` command with `setup.py`:

```shell
python setup.py test
```

Or, use `pytest` with customize options like:

```shell
pytest tests/test_openapi.py --maxfail=1
```

Furthermore, you can use `tox` to run tests with different environment configs to make sure the compatibility.

```shell
tox
```

After running tests, it will generate test reports under `test_reports/` which includes:

* test_reports/report.html: All outputs of test cases. You can trace the errors by this file if some test cases are failed.
* test_reports/coverage/index.html: Coverage report.

## Compatibility

Because this project is a plugin of `Sanic`, it is necessary to clarify which versions of `Sanic` and which versions of `Python` are supported. This is a compatibility matrix of `Sanic` and `Python`.:
|                   | Python 3.5 | Python 3.6 | Python 3.7 |
|------------------:|-----------:|------------|-----------:|
| Sanic 18.12 (LTS) |        Yes |        Yes |        Yes |
| Sanic 19.03       |        Yes |        Yes |        Yes |
| Sanic 19.06       |        No  |        Yes |        Yes |

Please make sure your contribution supports `Sanic 18.12` and `Python 3.5` **UNLESS** there is any specific need.

Some discussion of compatibility:

* [What position of this project](https://github.com/huge-success/sanic-openapi/issues/103#issuecomment-499463005)
* [Background story](https://community.sanicframework.org/t/should-we-bump-the-minimum-python-required-version-to-3-6/238/6?u=ahopkins)

## Swagger UI

This project includes all static files of `swagger-ui` under `sanic_openapi/ui/`. If you want to upgrade them, please describe which version of `swagger-ui` you want to use in `sanic_openapi/ui/version`. This would be very helpful to maintain the dependency of `swagger-ui` in this project.

## Code Style

In `dev` requirements, it already including some modules related to code style:

* black
* flake8
* isort

Please make sure your contribution will using the same styling tools. You can use following commands to apply them to your contributions:

```shell
black --verbose sanic_openapi tests
isort --recursive sanic_openapi tests
```

## Make a Pull Request

If you want to make a Pull Request, here are some suggestions:

1. Check other pull requests first, make sure your contributions are not duplicate to others.
2. Run all tests at your machine, make sure your contributions are works and does not break anything.
3. Document and example will be very appreciated.
