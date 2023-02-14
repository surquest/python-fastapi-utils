![GitHub](https://img.shields.io/github/license/surquest/python-fastapi-utils?style=flat-square)
![PyPI - Downloads](https://img.shields.io/pypi/dm/surquest-fastapi-utils?style=flat-square)
![PyPI](https://img.shields.io/pypi/v/surquest-fastapi-utils)

# Introduction

This project provides collection of utilities for FastAPI framework as:

* Custom Middlewares
* Exception Catchers
* Custom Routes

# Quick Start

This section shows how to use the utilities provided by this project:

```python
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from surquest.fastapi.utils.route import Route
from surquest.fastapi.utils.middleware import BasicMiddleware
from surquest.fastapi.utils.catcher import (
    catch_validation_exceptions,
    catch_http_exceptions,
)

app = FastAPI(
    title="Sample REST API application",
    openapi_url="/openapi.json"
)

# add middleware
app.add_middleware(BasicMiddleware) # this middleware writes request and response to the log

# exception handlers
app.add_exception_handler(HTTPException, catch_http_exceptions)
app.add_exception_handler(RequestValidationError, catch_validation_exceptions)

# custom routes
app.add_api_route(path="/", endpoint=Route.get_documentation, include_in_schema=False)
```


# Local development

You are more than welcome to contribute to this project. To make your start easier we have prepared a docker image with all the necessary tools to run it as interpreter for Pycharm or to run tests.


## Build docker image
```
docker build `
     --tag surquest/fastapi/utils `
     --file package.base.dockerfile `
     --target test .
```

## Run tests
```
docker run --rm -it `
 -v "${pwd}:/opt/project" `
 -e "GOOGLE_APPLICATION_CREDENTIALS=/opt/project/credentials/keyfile.json" `
 -w "/opt/project/test" `
 surquest/fastapi/utils pytest
```
