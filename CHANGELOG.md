# Changelog

### 0.6.1 (2020-01-03)


### Features

* **examples:** add class based routing demonstration in cars example ([df7724f](https://github.com/chenjr0719/sanic-openapi/commit/df7724fa344a8feefede5168541433e19e969b5c))
* **examples:** class based routing example ([9137de1](https://github.com/chenjr0719/sanic-openapi/commit/9137de14037778e0588853cb83a1ded2e645845f))
* fix for class based routing ([de21965](https://github.com/chenjr0719/sanic-openapi/commit/de21965a8e94e1f73efa8bd420a8d39367fa7f26))
* Provide ASGI compatibility through server event ([a6df84](https://github.com/huge-success/sanic-openapi/pull/130))
* Add basic support for type hinting-based docs ([ee640f](https://github.com/huge-success/sanic-openapi/pull/129))
* Basic support for TypedDicts (PEP 589) ([360a03](https://github.com/huge-success/sanic-openapi/pull/134))
* Support typing.Sequence and typing.List ([f80d19](https://github.com/huge-success/sanic-openapi/pull/136))
* Remove global variables ([3cdf88](https://github.com/huge-success/sanic-openapi/pull/140))
* removed field 'type': 'object' from swagger json when using doc.Object() ([60605c](https://github.com/huge-success/sanic-openapi/pull/149))

### Bug Fixes

* Allow empty list with List field ([74fd710](https://github.com/chenjr0719/sanic-openapi/commit/74fd71081a725d58545322dc2105c540de004529))
* fix example of class based view ([9c0bbd3](https://github.com/chenjr0719/sanic-openapi/commit/9c0bbd3a7e0ec2dfd999d6fbe14c2c1dedf36a29))
* Ignore routes under swagger blueprint ([ed932cc](https://github.com/chenjr0719/sanic-openapi/commit/ed932cca7286e59d8ac854a5dd0cf314c98ac688))
* fix typo in setup where sphinx-rtd-theme needed ([2e729e](https://github.com/huge-success/sanic-openapi/pull/139))

## 0.6.0 (2019-08-02)

### Features

* Add API module ([4a43817](https://github.com/huge-success/sanic-openapi/pull/111))
* Make it possible to register the same model definition multiple times in `doc.definitions` ([3c3329c](https://github.com/huge-success/sanic-openapi/pull/110))
* Support Swagger configuration ([a093d55](https://github.com/huge-success/sanic-openapi/pull/100))
* Super call added to List field serialize method ([93ab6fa](https://github.com/huge-success/sanic-openapi/pull/93))
* Support and examples for Class-Based Views (HTTPMethodView) ([de21965](https://github.com/huge-success/sanic-openapi/pull/64))
* Add operation decorator ([039a0db](https://github.com/huge-success/sanic-openapi/pull/95))
* Add a if-statement at build_spec checking add default 200 response or not ([1d8d7d0](https://github.com/huge-success/sanic-openapi/pull/116))
* Add File field & Fix some line with black style ([06c662b](https://github.com/huge-success/sanic-openapi/pull/120))

### Bug Fixes

* Allow empty list with List field ([74fd710](https://github.com/chenjr0719/sanic-openapi/commit/74fd710))
* fix example of class based view ([9c0bbd3](https://github.com/chenjr0719/sanic-openapi/commit/9c0bbd3))
* Ignore routes under swagger blueprint ([ed932cc](https://github.com/chenjr0719/sanic-openapi/commit/ed932cc))
* fix static and exclude ([5a8aab8](https://github.com/huge-success/sanic-openapi/pull/80))


### Build System

* Add version file under sanic_openapi ([020338b](https://github.com/chenjr0719/sanic-openapi/commit/020338b))
* Fix regex of version in setup.py ([ab01896](https://github.com/chenjr0719/sanic-openapi/commit/ab01896))
* Use setup.py to control dependencies and remove requirements files ([1079e15](https://github.com/chenjr0719/sanic-openapi/commit/1079e15))


### Tests

* Add clean up in app fixture ([fa1b111](https://github.com/chenjr0719/sanic-openapi/commit/fa1b111))
* Add config of coverage and integrate with setup.py ([30a9915](https://github.com/chenjr0719/sanic-openapi/commit/30a9915))
* Add Sanic 19.06 to tox env ([8ad28cf](https://github.com/chenjr0719/sanic-openapi/commit/8ad28cf))
* Add serialize_schema tests ([43b4c9d](https://github.com/chenjr0719/sanic-openapi/commit/43b4c9d))
* Add test cases ([17ba469](https://github.com/chenjr0719/sanic-openapi/commit/17ba469))
* Add tests for base fields ([2254f23](https://github.com/chenjr0719/sanic-openapi/commit/2254f23))
* Add tests for decorators ([063afc3](https://github.com/chenjr0719/sanic-openapi/commit/063afc3))
* Add tests for JsonBody field, List field, and Object field ([2a9f4d5](https://github.com/chenjr0719/sanic-openapi/commit/2a9f4d5))
* Fix redirect test ([1539b04](https://github.com/chenjr0719/sanic-openapi/commit/1539b04))
* Modify envlist in tox.ini to check compatibility of Sanic releases ([2c518b6](https://github.com/chenjr0719/sanic-openapi/commit/2c518b6))
* Remove skip of static test case and fix options route test ([86a8a4a](https://github.com/chenjr0719/sanic-openapi/commit/86a8a4a))
