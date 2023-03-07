import sys
import secrets
import random
import contextvars
from starlette.requests import Request
from google.cloud.logging_v2.handlers._helpers import _parse_xcloud_trace

CLOUD_TRACE_CONTEXT = contextvars.ContextVar(
    'CLOUD_TRACE_CONTEXT',
    default=""
)

HTTP_REQUEST_CONTEXT = contextvars.ContextVar(
    'HTTP_REQUEST_CONTEXT',
    default=dict({})
)

class HTTPContext(object):
    """HTTP Context

    This class is used to set the HTTP Request Context and Cloud Trace Context
    for given request.
    """

    @staticmethod
    async def set_cloud_trace_context(request: Request):
        """Set the Cloud Trace Context for given request."""

        trace = HTTPContext.get_cloud_trace_context(request=request)

        if trace is not None:

            CLOUD_TRACE_CONTEXT.set(trace)

    @staticmethod
    async def set_http_request_context(request: Request):
        """Set the HTTP Request Context for given request."""

        try:
            body = await request.json()
        except BaseException:
            body =  await request.body()
            body = body.decode('utf-8')

        http_request = {
            'requestMethod': request.method,
            'requestUrl': request.url,
            'body': body,
            'paramsPatch': dict(request.path_params),
            'paramsQuery': dict(request.query_params),
            "headers": dict(request.headers),
            "cookies": dict(request.cookies),
            'requestSize': sys.getsizeof(request),
            'remoteIp': request.client.host,
            'protocol': request.url.scheme,
        }

        if 'referrer' in request.headers:
            http_request['referrer'] = request.headers.get('referrer')

        if 'user-agent' in request.headers:
            http_request['userAgent'] = request.headers.get('user-agent')

        HTTP_REQUEST_CONTEXT.set(http_request)

    @staticmethod
    def get_cloud_trace_context(request: Request):
        """Extract the trace context from the request headers."""

        if 'X-Cloud-Trace-Context' in request.headers:

            return request.headers.get('X-Cloud-Trace-Context')


    @staticmethod
    def get_trace_context():
        """Get the trace context from the context variable."""

        trace_id, span_id, flags = _parse_xcloud_trace(
            CLOUD_TRACE_CONTEXT.get()
        )
        if trace_id is None:
            trace_id = secrets.token_hex(16)
        if span_id is None:
            span_id = str(random.getrandbits(64))
        return trace_id, span_id, flags