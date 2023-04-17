import os
import json
import logging
import datetime as dt
import google.cloud.logging
from surquest.fastapi.utils.GCP.http_context import (
    HTTPContext
)

from .http_context import (
    HTTP_REQUEST_CONTEXT
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

    GCP_LOG_TYPE = "type.googleapis.com/type.googleapis.com/google.devtools.clouderrorreporting.v1beta1.ReportedErrorEvent"

    def __init__(
            self,
            fields = {
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

        # convert log record to dictionary compatible with GCP LogRecord format
        log = self.format_log_entry(record)

        # if log record is an error add @type attribute to comply with GCP Error Reporting format
        if record.levelno >= logging.ERROR:

            tb = [] # empty traceback
            if "ctx" in log and "traceback" in log["ctx"]:
                # get traceback from log record if present
                tb = log["ctx"]["traceback"]

            log["@type"] = self.GCP_LOG_TYPE
            log["message"] = self.format_stack_trace(
                message=log["message"],
                traceback=tb
            )
            log["serviceContext"] = self.get_service_context()
            log["context"] = {
                "httpRequest": self.get_http_request_context(),
                "reportLocation": self.get_report_location(record),
                "user": self.get_user()
            }

        return json.dumps(log, default=str)

    @staticmethod
    def get_user():
        """Methods returns user context in case of running the service on GCP
        behind Google Identity Aware Proxy
        """

        email = "unknown"
        request = HTTP_REQUEST_CONTEXT.get()

        if isinstance(request.get("headers"), dict):
            email = request.get("headers").get(
                "x-goog-authenticated-user-email",
                email
            )

        return email

    @staticmethod
    def get_service_context():
        """Methods returns service context in case of running the service on GCP"""

        return {
            "service": os.getenv("K_SERVICE", "LOCAL"),
            "version": os.getenv("K_REVISION", "-")
        }

    @staticmethod
    def get_http_request_context():
        """Methods returns http request context in case of running the service on GCP"""

        request = HTTP_REQUEST_CONTEXT.get()

        return {
            "method": request.get("requestMethod"),
            "url": str(request.get("requestUrl")),
            "userAgent": request.get("userAgent"),
            "referrer": request.get("referrer"),
            "responseStatusCode": 500,
            "remoteIp": request.get("remoteIp")
        }

    @staticmethod
    def format_stack_trace(message, traceback: list) -> str:
        """Method to format traceback to comply with GCP Error Reporting format"""

        stack_trace = [F"{message}:"]
        for i in traceback:
            if "^^" in i:
                # stack_trace.append("")
                pass
            else:
                stack_trace.append(i)

        return "\n".join(stack_trace)

    @staticmethod
    def get_report_location(record):
        """Methods returns location within the application code that reported the error"""

        return {
            "filePath": record.pathname,
            "lineNumber": record.lineno,
            "functionName": record.funcName
        }

    @staticmethod
    def get_extra(record):
        """
        Get extra attributes from the LogRecord
        """
        return {
            key: val for key, val in record.__dict__.items()
            if key not in JSONFormatter.LOG_RECORDS_ATTRS
        }
