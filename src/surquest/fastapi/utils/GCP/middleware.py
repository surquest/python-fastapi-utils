# import external modules
from starlette.requests import Request
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint
)

# import internal modules
from .catcher import Catcher
from .http_context import HTTPContext
from .logging import setup_logging


__all__ = [
    "BasicMiddleware",
    "LoggingMiddleware",
    "DBMiddleware"
]

class BasicMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)

    @staticmethod
    async def dispatch(
            request: Request,
            call_next: RequestResponseEndpoint
    ):

        try:

            response = await call_next(request)
            return response

        except BaseException as exc:

            return await Catcher.catch_internal_error(request, exc)

class LoggingMiddleware(BaseHTTPMiddleware):

    def __init__(self, app):
        super().__init__(app)

    @staticmethod
    async def dispatch(
            request: Request,
            call_next: RequestResponseEndpoint
    ):

        await HTTPContext.set_cloud_trace_context(request)
        await HTTPContext.set_http_request_context(request)

        setup_logging()

        try:

            response = await call_next(request)
            return response

        except BaseException as exc:

            return await Catcher.catch_internal_error(request, exc)


class DBMiddleware(BaseHTTPMiddleware):

    def __init__(self, app, db=None, ):
        super().__init__(app)
        self.db = db

    async def dispatch(self, request: Request, call_next):

        try:

            await HTTPContext.set_cloud_trace_context(request)
            await HTTPContext.set_http_request_context(request)

            setup_logging()

            request.state.db_engine = self.db.get_engine()

            response = await call_next(request)
            return response

        except BaseException as exc:

            return await Catcher.catch_internal_error(request, exc)

        finally:

            request.state.db_engine.dispose()
