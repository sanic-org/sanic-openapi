# Changelog

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
