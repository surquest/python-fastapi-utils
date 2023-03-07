# import pytest
# import json
# from starlette.requests import Request
# from starlette.datastructures import Headers
# from surquest.fastapi.utils.catcher import Catcher

class TestCase:

    def test__JSONFormatter(self):

        assert 1 == 1

# def build_request(
#     method: str = "GET",
#     server: str = "www.example.com",
#     path: str = "/",
#     headers: dict = None,
#     body: str = None,
# ) -> Request:
#     if headers is None:
#         headers = {}
#     request = Request(
#         {
#             "type": "http",
#             "path": path,
#             "headers": Headers(headers).raw,
#             "http_version": "1.1",
#             "method": method,
#             "scheme": "https",
#             "client": ("127.0.0.1", 8080),
#             "server": (server, 443),
#         }
#     )
#     if body:
#
#         async def request_body():
#             return body
#
#         request.body = request_body
#     return request
# class TestLogger:
#
#     ERRORS = {
#         "value": "Wrong value: Expected: `{}`, Actual: `{}`",
#         "type": "Wrong type: Expected: `{}`, Actual: `{}`"
#     }
#
#     @pytest.mark.asyncio
#     async def test__get_request_body(self):
#
#         catcher = Catcher()
#         body = {'key': 'value'}
#
#         assert body == await catcher.get_request_body(
#             request=build_request(
#                 method="POST",
#                 body=json.dumps(body)
#             )
#         )

