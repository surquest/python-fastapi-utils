![GitHub](https://img.shields.io/github/license/surquest/python-fastapi-utils?style=flat-square)
![PyPI - Downloads](https://img.shields.io/pypi/dm/surquest-fastapi-utils?style=flat-square)
![PyPI](https://img.shields.io/pypi/v/surquest-fastapi-utils)

# Introduction

This project provides collection of utilities for smooth integration of FastAPI framework with Google Cloud Platform services as logging and tracing.

The key features of this project are:

* Logging to Cloud Logging
* Tracing to Cloud Logging
* Error Reporting via Cloud Logging
* Custom middleware for configuration of logging
* Custom exception handlers treating HTTP and validation exceptions
* Custom routes for documentation and favicon
* Custom responses with statuses `success`, `warning` and `error` and standardized error messages

# Quick Start

This section shows how to use the utilities provided by this project:

```python
"""File main.py with FastAPI app"""
import os
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from fastapi import FastAPI, Request, Query

# import surquest modules and objects
from surquest.fastapi.utils.route import Route  # custom routes for documentation and FavIcon
from surquest.fastapi.utils.GCP.tracer import Tracer
from surquest.fastapi.utils.GCP.logging import Logger
from surquest.fastapi.schemas.responses import Response
from surquest.fastapi.utils.GCP.middleware import LoggingMiddleware
from surquest.fastapi.utils.GCP.catcher import (
    catch_validation_exceptions,
    catch_http_exceptions,
)

PATH_PREFIX = os.getenv('PATH_PREFIX','')

app = FastAPI(
    title="Exchange Rates ETL",
    openapi_url=F"{PATH_PREFIX}/openapi.json"
)

# add middleware
app.add_middleware(LoggingMiddleware)

# exception handlers
app.add_exception_handler(HTTPException, catch_http_exceptions)
app.add_exception_handler(RequestValidationError, catch_validation_exceptions)

# custom routes to documentation and favicon
app.add_api_route(path=F"{PATH_PREFIX}/", endpoint=Route.get_documentation, include_in_schema=False)
app.add_api_route(path=PATH_PREFIX, endpoint=Route.get_favicon, include_in_schema=False)

# custom route to illustrate logging and tracing
@app.get(F"{PATH_PREFIX}/users")
async def get_users(
    age: int = Query(
        default=18,
        description="Minimal age of the user",
        example=30,

    ),
):

    with Tracer.start_span("Generate users"):

        users = [
            {"name": "John Doe", "age": 30, "email": "john@doe.com"},
            {"name": "Will Smith", "age": 42, "email": "will@smith.com"}
        ]

        Logger.info('Found %s users', len(users), extra={"users": users})

    with Tracer.start_span("Filtering users"):

        output = []
        excluded = []
        Logger.debug(F"Filtering users by age > {age}")

        for user in users:

            if user["age"] > age:
                output.append(user)
            else:
                excluded.append(user)

        Logger.debug(
            'Number of excluded users: %s', len(excluded),
            extra={"excluded": excluded}
        )

    return Response.set(data=output)
```

The endpoint `/users` will return the following standard response:

```json
{
  "info": {
    "status": "success"
  },
  "data": [
    {
      "name": "John Doe",
      "age": 30,
      "email": "john@doe.com"
    },
    {
      "name": "Will Smith",
      "age": 42,
      "email": "will@smith.com"
    }
  ]
}
```

and the logs will are available in Google Cloud Platform console within Stackdriver Logging:

![Log Entries](https://github.com/surquest/python-fastapi-utils/blob/main/assets/img/logs.png?raw=true)

as well as the traces are available in Google Cloud Platform console within Stackdriver Trace:

![Trace](https://github.com/surquest/python-fastapi-utils/blob/main/assets/img/trace.png?raw=true)


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
