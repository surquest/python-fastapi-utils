import os
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse


class Route(object):

    @staticmethod
    def get_favicon(
            path: str = os.getenv('FAVICON','/opt/project/app/static/favicon.ico')
    ):
        return FileResponse(path)

    @staticmethod
    def get_documentation(title: str = 'API Documentation'):
        return get_swagger_ui_html(
            openapi_url=F"{os.getenv('PATH_PREFIX','')}/openapi.json",
            title=title
        )
