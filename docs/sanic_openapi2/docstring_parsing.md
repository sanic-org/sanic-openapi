# Docstring Parsing

sanic-openAPI will try to parse your function for documentation to add to the swagger interface, so for example:

```python
app = Sanic()
app.blueprint(openapi2_blueprint)


@app.get("/test")
async def test(request):
	'''
	This route is a test route

	In can do lots of cool things
	'''
    return json({"Hello": "World"})
```

Would add that docstring to the openAPI route 'summary' and 'description' fields.

For advanced users, you can also edit the yaml yourself, by adding the line "openapi:" followed by a valid yaml string.

Note: the line "openapi:" should contain no whitespace before or after it.

Note: any decorators you use on the function must utilise functools.wraps or similar in order to preserve the docstring if you would like to utilising the docstring parsing capability.

```python
app = Sanic()
app.blueprint(openapi2_blueprint)


@app.get("/test")
async def test(request):
	'''
	This route is a test route

	In can do lots of cool things

	openapi:
	---
	responses:
	  '200':
	    description: OK
	'''
    return json({"Hello": "World"})
```

If the yaml fails to parse for any reason, a warning will be printed, and the yaml will be ignored.
