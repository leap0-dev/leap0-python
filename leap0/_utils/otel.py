from __future__ import annotations

import asyncio
import functools
import time
from typing import Any, Callable, TypeVar, cast

from opentelemetry import metrics, trace
from opentelemetry.trace import Status, StatusCode

F = TypeVar("F", bound=Callable[..., Any])

_tracer = None
_meter = None
_histograms: dict[str, Any] = {}


def get_tracer() -> Any:
    """Return the SDK OpenTelemetry tracer singleton."""
    global _tracer
    if _tracer is None:
        _tracer = trace.get_tracer("leap0-sdk-python")
    return _tracer


def get_meter() -> Any:
    """Return the SDK OpenTelemetry meter singleton."""
    global _meter
    if _meter is None:
        _meter = metrics.get_meter("leap0-sdk-python")
    return _meter


def _metric_name(name: str) -> str:
    return name.replace(".", "_").lower()


def with_instrumentation(name: str) -> Callable[[F], F]:
    """Instrument a function with OpenTelemetry spans and duration metrics."""
    def decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                tracer = get_tracer()
                meter = get_meter()
                histogram_name = _metric_name(name)
                histogram = _histograms.get(histogram_name)
                if histogram is None:
                    histogram = meter.create_histogram(
                        f"{histogram_name}_duration",
                        description=f"Duration of {name}",
                        unit="ms",
                    )
                    _histograms[histogram_name] = histogram

                start = time.time()
                with tracer.start_as_current_span(name) as span:
                    try:
                        result = await func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        histogram.record((time.time() - start) * 1000, {"status": "success"})
                        return result
                    except Exception as exc:
                        span.set_status(Status(StatusCode.ERROR, str(exc)))
                        span.record_exception(exc)
                        histogram.record((time.time() - start) * 1000, {"status": "error"})
                        raise

            return cast(F, async_wrapper)

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            tracer = get_tracer()
            meter = get_meter()
            histogram_name = _metric_name(name)
            histogram = _histograms.get(histogram_name)
            if histogram is None:
                histogram = meter.create_histogram(
                    f"{histogram_name}_duration",
                    description=f"Duration of {name}",
                    unit="ms",
                )
                _histograms[histogram_name] = histogram

            start = time.time()
            with tracer.start_as_current_span(name) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    histogram.record((time.time() - start) * 1000, {"status": "success"})
                    return result
                except Exception as exc:
                    span.set_status(Status(StatusCode.ERROR, str(exc)))
                    span.record_exception(exc)
                    histogram.record((time.time() - start) * 1000, {"status": "error"})
                    raise

        return cast(F, sync_wrapper)

    return decorator
