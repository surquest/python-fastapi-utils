# import external modules
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from traceback import format_exc

from surquest.fastapi.schemas.responses import Response, Message
from surquest.GCP.logger import Logger


__all__ = [
    "Catcher",
    "catch_validation_exceptions",
    "catch_http_exceptions",
    "catch_base_exceptions"
]


async def catch_base_exceptions(request, exc):

    try:

        # evaluate request body to be able to log it in case of error
        # IMPORTANT: does not work well for streaming requests
        await Catcher.dispatch_request_body(
            request=request,
            body=await request.body()
        )

        response = await call_next(request)
        return response

    except BaseException as e:

        return await Catcher.catch_internal_error(request, e)

async def catch_validation_exceptions(request, exc):

    return Catcher.catch_validation_error(request, exc)


async def catch_http_exceptions(request, exc):

    return Catcher.catch_http_exception(request, exc)


class Catcher(object):
    @classmethod
    async def catch_internal_error(cls, request: Request, exc: Exception, body=None):

        if body is None:

            body = await cls.get_request_body(request=request)

        message = Message(
            msg=str(exc),
            type="server.error",
            ctx={"traceback": str(format_exc()).split("\n")},
        )

        cls.log_error(
            request=request, errors=message.dict(exclude_none=True), body=body
        )

        return Response.set(
            status_code=500,
            errors=[message]
        )

    @classmethod
    def catch_validation_error(cls, request: Request, exc: RequestValidationError):

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

        cls.log_error(request=request, errors=errors, body=exc.body)

        return Response.set(
            status_code=422,
            errors=errors
        )

    @classmethod
    def catch_http_exception(cls, request: Request, exc: StarletteHTTPException):

        loc = getattr(exc, "loc", [str(request.url)])
        msg = getattr(exc, "detail", "Not Found")
        type_ = getattr(exc, "type", "not.found")
        ctx = getattr(exc, "ctx", {})

        message = Message(
            msg=msg,
            type=type_,
            loc=loc,
            ctx=ctx
        )

        try:
            body = exc.body
        except BaseException:
            body = None

        cls.log_error(
            request=request, errors=message.dict(exclude_none=True), body=body
        )

        return Response.set(
            status_code=404,
            errors=[message]
        )

    @classmethod
    def log_error(cls, request, errors, body=None):

        logger = Logger(request)

        logger.debug(
            msg="Request details",
            **{
                "request": {
                    "method": request.method,
                    "url": str(request.url),
                    "body": body,
                    "query_params": dict(request.query_params),
                    "path_params": dict(request.path_params),
                    "client": request.client,
                    "headers": dict(request.headers),
                    "cookies": dict(request.cookies),
                }
            }
        )

        logger.error(
            msg="Ops, something went wrong",
            **{"errors": errors}
        )

    @staticmethod
    async def dispatch_request_body(request: Request, body: bytes):
        """Method set request body"""

        async def receive():
            return {"type": "http.request", "body": body}

        request._receive = receive

    @staticmethod
    async def get_request_body(request: Request) -> bytes:
        """Method return request body"""

        try:
            return await request.json()
        except BaseException:
            return await request.body()
