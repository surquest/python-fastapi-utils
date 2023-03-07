import json
import logging
import datetime as dt
import google.cloud.logging
from surquest.fastapi.utils.GCP.http_context import (
    HTTPContext
)

__all__ = ["JSONFormatter"]


class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the LogRecord.
    """

    LOG_RECORDS_ATTRS = {
        "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
        "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
        "created", "msecs", "relativeCreated", "thread", "threadName",
        "process", "processName", "message", "asctime"
    }

    def __init__(
            self,
            fields: dict = {
                "severity": "levelname",
                "message": "message",
                "ctx": "ctx",
                "logging.googleapis.com/trace": "trace",
                "logging.googleapis.com/spanId": "spanId",
                "logging.googleapis.com/trace_sampled": "flags",
                "logging.googleapis.com/sourceLocation": "source"
            }
    ):
        super().__init__(fmt=None, datefmt=None, style='%')
        self.project_id = "-"
        self.fields = fields

        try:
            self.client = google.cloud.logging.Client()
            self.project_id = self.client.project
        except Exception:
            pass

    def format_log_entry(self, record: logging.LogRecord) -> dict:
        """Method to extract from LogRecord all attributes required attributes
        specified in self.fields and format them to comply with GCP LogRecord format

        :param record: LogRecord
        :return: dictionary with required fields
        :rtype: dict
        """
        return {
            key: record.__dict__[val] \
            for key, val in self.fields.items()
        }

    @staticmethod
    def format_created_at(timestamp: float) -> str:
        """Method to format timestamp to ISO 8601 format"""
        return dt.datetime.fromtimestamp(timestamp).isoformat()

    def format(self, record) -> str:
        """Method to format LogRecord to comply with GCP LogRecord format
        specified in https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry

        :param record:
        :return:
        """

        # get log message
        record.message = record.getMessage()

        # collect all attributes passed to LogRecord via logging.info(..., extra=...)
        # into json_field to comply with GCP LogRecord format https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry
        record.ctx = self.get_extra(record)  # context

        # extend LogRecord attributes by trace information
        (
            trace_id,
            span_id,
            flags
        ) = HTTPContext.get_trace_context()

        record.trace = f"projects/{self.project_id}/traces/{trace_id}"
        record.spanId = span_id
        record.flags = flags

        # add information about the location of the source of the log entry
        record.source = {
            "file": record.pathname,
            "function": record.funcName,
            "line": record.lineno,
        }

        #
        message_dict = self.format_log_entry(record)

        return json.dumps(message_dict, default=str)

    @staticmethod
    def get_extra(record):
        """
        Get extra attributes from the LogRecord
        """
        return {
            key: val for key, val in record.__dict__.items()
            if key not in JSONFormatter.LOG_RECORDS_ATTRS
        }
