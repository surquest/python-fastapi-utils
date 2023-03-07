from .base import Base
from typing import List, Optional
from .status import Status
from .message import Message
from .metadata import Metadata


class InfoSuccess(Base):
    status: str = Status.success
    metadata: Optional[Metadata] = None


class InfoWarning(Base):
    status: str = Status.warning
    metadata: Optional[Metadata] = None
    warnings: List[Message] = []


class InfoError(Base):
    status: str = Status.error
    warnings: Optional[List[Message]] = None
    errors: List[Message] = []
