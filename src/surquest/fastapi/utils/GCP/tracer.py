import os
from opentelemetry import trace
from opentelemetry.trace import NonRecordingSpan
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider, SpanContext, RandomIdGenerator
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ALWAYS_ON

from .http_context import (
    HTTPContext
)

__all__ = [
    "Tracer"
]

DEFAULT_TRACER_NAME = os.getenv('APP_NAME', "APILogger")

tracer_provider = TracerProvider(sampler=ALWAYS_ON)  # always trace
trace.set_tracer_provider(tracer_provider)
# cloud_trace_exporter = CloudTraceSpanExporter()
try:
    cloud_trace_exporter = CloudTraceSpanExporter()
except Exception as e:
    print("CloudTraceSpanExporter not initialized")
    print(e)
    cloud_trace_exporter = None

if cloud_trace_exporter is not None:    
    tracer_provider.add_span_processor(
        # BatchSpanProcessor buffers spans and sends them in batches in a
        # background thread. The default parameters are sensible, but can be
        # tweaked to optimize your performance
        BatchSpanProcessor(cloud_trace_exporter)
    )

class Tracer:

    @classmethod
    def start_span(cls, name):

        (
            trace_id,
            span_id,
            flags
        ) = HTTPContext.get_trace_context()

        span_context = SpanContext(
            trace_id=int(trace_id, base=16),
            span_id=RandomIdGenerator().generate_span_id(),
            is_remote=False,
        )
        ctx = trace.set_span_in_context(NonRecordingSpan(span_context))
        return trace.get_tracer(DEFAULT_TRACER_NAME).start_as_current_span(name=name, context=ctx)
