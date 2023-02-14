from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse
import os


class Route(object):

    @staticmethod
    def get_favicon(
            path: str = f"{os.getenv('APP_HOME')}/app/static/favicon.ico"
    ):
        return FileResponse(path)

    @staticmethod
    def get_documentation(title: str = 'API Documentation'):
        return get_swagger_ui_html(
            openapi_url="./openapi.json",
            title=title
        )
