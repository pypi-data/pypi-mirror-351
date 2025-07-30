from functools import wraps
from inspect import iscoroutinefunction
from pydantic import BaseModel
from opentelemetry.sdk.trace import Tracer, Span


def _set_func_span_attributes(span: Span, *args, **kwargs):
    span.set_attribute("function.args", str(args))
    span.set_attribute("function.kwargs", str(kwargs))


def _set_func_span_result_attributes(span: Span, result):
    if isinstance(result, BaseModel):
        span.set_attribute("function.result", str(result.model_dump()))
    else:
        span.set_attribute("function.result", str(result))


# Wrap any function with a Tracer to record Spans. Works with both sync and async functions
# Automatically captures function arguments and outputs
def auto_trace(tracer: Tracer, name: str):
    def decorator(func):
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(name) as span:
                # Add input arguments to the span
                _set_func_span_attributes(span, args, kwargs)
                # Execute the function
                result = func(*args, **kwargs)
                # set function output result in span
                _set_func_span_result_attributes(span, result)
                return result

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(name) as span:
                # Add input arguments to the span
                _set_func_span_attributes(span, args, kwargs)
                # Execute the function
                result = await func(*args, **kwargs)
                # set function output result in span
                _set_func_span_result_attributes(span, result)
                return result

        # Pick the wrapper to use if the function is async or not
        if iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
