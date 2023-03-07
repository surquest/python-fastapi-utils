from pydantic import BaseModel

class Base(BaseModel):
    """Base class for all responses:

    This class ensures that all undefined fields are excluded from the response

    """
    def dict(self, *args, **kwargs):
        if kwargs:
            kwargs["exclude_none"] = True

        return BaseModel.dict(self, *args, **kwargs)