from .base import Base
from .info import InfoSuccess, InfoWarning, InfoError
from typing import Union, List, Dict, Optional
from starlette.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder


class Success(Base):
    info: InfoSuccess = InfoSuccess()
    data: Optional[Union[List, Dict]]= None

    @classmethod
    def set(cls, data, metadata=None):
        return cls(
            info=InfoSuccess(metadata=metadata),
            data=data
        )


class Warnings(Base):

    info: InfoWarning = InfoWarning()
    data: Optional[Union[List, Dict]] = None

    @classmethod
    def set(cls, warnings, data, metadata=None):

        return cls(
            info=InfoWarning(warnings=warnings, metadata=metadata),
            data=data
        )


class Errors(Base):
    info: InfoError = InfoError()

    @classmethod
    def set(cls, errors, warnings=None):
        return cls(
            info=InfoError(
                warnings=warnings,
                errors=errors
            )
        )

class Response:

    @classmethod
    def set(
        cls,
        status_code=None,
        data=None,
        metadata=None,
        warnings=None,
        errors=None
    ):

        status_code = cls.get_status_code(status_code, warnings, errors)

        if errors is not None:

            return JSONResponse(
                status_code=status_code,
                content=jsonable_encoder(
                    Errors.set(
                        errors=errors,
                        warnings=warnings
                    )
                )
            )
        if errors is None and warnings is not None:

            return JSONResponse(
                status_code=status_code,
                content=jsonable_encoder(
                    Warnings.set(
                        warnings=warnings,
                        data=data,
                        metadata=metadata
                    )
                )
            )

        return JSONResponse(
            status_code=status_code,
            content=jsonable_encoder(
                Success.set(
                    data=data,
                    metadata=metadata
                )
            )
        )

    @staticmethod
    def get_status_code(status_code, warnings, errors):

        if isinstance(status_code, int):
            return status_code

        if errors is not None:
            return 500

        if errors is None and warnings is not None:
            return 299

        return 200

class Responses:

    @classmethod
    def get(cls):

        return {
            200: {"model": Success},
            299: {"model": Warnings},
            400: {"model": Errors},
            422: {"model": Errors},
            500: {"model": Errors},
        }
