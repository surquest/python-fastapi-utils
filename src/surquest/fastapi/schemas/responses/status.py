from enum import Enum


class Status(str, Enum):

    success = "success"
    warning = "warning"
    error = "error"
