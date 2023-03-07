from pydantic import Field
from .base import Base

class Metadata(Base):

    offset: int = Field(
        default=0,
        title="Offset",
        description="Number of records to skip from the beginning",
        ge=0,
        example=0,
    )

    limit: int = Field(
        default=0,
        title="Offset",
        description="Number of records to skip from the beginning",
        ge=0,
        example=0,
    )

    count: int = Field(
        ...,
        title="Count of records",
        description="Count of records returned by the call",
        example=391,
        ge=0,
    )

    total: int = Field(
        ...,
        title="Total records",
        description="Total number of records in the database",
        example=18301,
        ge=0,
    )
