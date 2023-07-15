# import external modules
import os
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback

from surquest.fastapi.schemas.responses import Response, Message

from .logging import Logger
from .http_context import (
    HTTP_REQUEST_CONTEXT,
    CLOUD_TRACE_CONTEXT
)

__all__ = [
    "Catcher",
    "catch_validation_exceptions",
    "catch_http_exceptions"
]


async def catch_validation_exceptions(request: Request, exc):
    return await Catcher.catch_validation_error(request, exc)


async def catch_http_exceptions(request: Request, exc):
    return await Catcher.catch_http_exception(request, exc)


class Catcher:

    OUPS = "Oups, something went wrong"

    @classmethod
    async def catch_internal_error(
            cls,
            request: Request,
            exc: BaseException
    ):

        tb = traceback.format_exc(chain=False).split("\n")

        ctx = {
            "trace": CLOUD_TRACE_CONTEXT.get()
        }

        if os.getenv("ENV", "DEV").upper() not in ["PROD", "PRODUCTION"] or \
            os.getenv("ENVIRONMENT", "DEV").upper() not in ["PROD", "PRODUCTION"]:

            ctx["traceback"] = tb

        message = Message(
            msg=F"{str(exc)} ({type(exc).__name__})",
            type="SERVER.ERROR",
            ctx=ctx,
        )

        Logger.error(
            F"{str(exc)} ({type(exc).__name__})",
            extra={
                "error": message.dict(exclude_none=True),
                "request": HTTP_REQUEST_CONTEXT.get(),
                "traceback": tb
            }
        )

        return Response.set(
            status_code=500,
            errors=[message]
        )

    @classmethod
    async def catch_validation_error(
            cls,
            request: Request,
            exc: RequestValidationError
    ):
        errors = []

        for error in exc.errors():
            errors.append(
                Message(
                    msg=error.get("msg"),
                    type=error.get("type"),
                    loc=error.get("loc"),
                    ctx=error.get("ctx"),
                ).dict(exclude_none=True)
            )

        Logger.error(
            "Validation Error",
            extra={
                "errors": errors,
                "request": HTTP_REQUEST_CONTEXT.get()
            }
        )

        return Response.set(
            status_code=422,
            errors=errors
        )

    @classmethod
    async def catch_http_exception(
            cls,
            request: Request,
            exc: StarletteHTTPException
    ):

        message = Message(
            msg=getattr(exc, "detail", f"Not Found: ({request.url})"),
            type=getattr(exc, "type", "NOT.FOUND"),
            loc=getattr(exc, "loc", [F"{request.url}"]),
            ctx=getattr(exc, "ctx", {"trace": CLOUD_TRACE_CONTEXT.get()})
        )

        Logger.error(
            F"{message.msg}: ({message.loc[0]})",
            extra={
                "error": message.dict(exclude_none=True),
                "request": HTTP_REQUEST_CONTEXT.get()
            }
        )

        return Response.set(
            status_code=getattr(exc, "status_code", 404),
            errors=[message]
        )
