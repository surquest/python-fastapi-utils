import typing
from fastapi.security.api_key import APIKeyQuery
from fastapi import HTTPException, Security, Request


api_key_query = APIKeyQuery(name="apiKey", auto_error=False)

async def check_api_key(
    request: Request,
    api_key_query: str = Security(api_key_query),
):

    # check if app has defined API key
    if "api_key" in request.app.extra:

        # check if passed API key is equal to app's API key
        if api_key_query == request.app.extra.get("api_key"):
            return api_key_query
        else:
            raise AUTHException()


class AUTHException(HTTPException):
    def __init__(
        self,
        status_code: int = 401, # HTTP status code for Unauthorized
        detail: typing.Optional[str] = "Unauthorized: Invalid API Key",
        loc: typing.Optional[list] = ["query", "apiKey"],
        type: typing.Optional[str] = "AUTH.ERROR"
    ) -> None:
        self.status_code = status_code
        self.detail = detail
        self.loc = loc
        self.type = type

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, detail={self.detail!r})"