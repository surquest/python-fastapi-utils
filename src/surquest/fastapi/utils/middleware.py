# import external modules
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# import internal modules
from surquest.fastapi.utils.catcher import Catcher


class BasicMiddleware(BaseHTTPMiddleware):
    def __init__(
            self,
            app
    ):
        super().__init__(app)

    @staticmethod
    async def dispatch(request: Request, call_next):

        try:

            # evaluate request body to be able to log it in case of error
            # IMPORTANT: does not work well for streaming requests
            await Catcher.dispatch_request_body(
                request=request,
                body=await request.body()
            )

            response = await call_next(request)
            return response

        except BaseException as exc:

            return await Catcher.catch_internal_error(request, exc)


class DBMiddleware(BaseHTTPMiddleware):

    def __init__(
            self,
            app,
            db=None,
    ):
        super().__init__(app)
        self.db = db

    async def dispatch(self, request: Request, call_next):

        try:
            request.state.db_engine = self.db.get_engine()

            # evaluate request body to be able to log it in case of error
            # IMPORTANT: does not work well for streaming requests
            await Catcher.dispatch_request_body(
                request=request,
                body=await request.body()
            )

            response = await call_next(request)

            return response

        except BaseException as exc:

            return await Catcher.catch_internal_error(request, exc)

        finally:

            request.state.db_engine.dispose()
