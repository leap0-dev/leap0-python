from __future__ import annotations

import asyncio
import functools
import threading
import time
from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import ParamSpec, Protocol, TypeVar, cast

from opentelemetry import metrics, trace
from opentelemetry.trace import Status, StatusCode

P = ParamSpec("P")
R = TypeVar("R")


class _HistogramProtocol(Protocol):
    """Protocol for OpenTelemetry histograms used by the SDK."""

    def record(self, amount: float, attributes: dict[str, str]) -> None:
        """Record a duration value with metric attributes."""
        ...


class _MeterProtocol(Protocol):
    """Protocol for OpenTelemetry meters used by the SDK."""

    def create_histogram(self, name: str, *, description: str, unit: str) -> _HistogramProtocol:
        """Create a histogram instrument."""
        ...


class _SpanProtocol(Protocol):
    """Protocol for spans created by the SDK tracer."""

    def set_status(self, status: Status) -> None:
        """Set the status on the current span."""
        ...

    def record_exception(self, exception: BaseException) -> None:
        """Attach an exception to the current span."""
        ...


class _SpanContextManagerProtocol(Protocol):
    """Protocol for context managers that yield spans."""

    def __enter__(self) -> _SpanProtocol:
        """Enter the span context."""
        ...

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool | None:
        """Exit the span context."""
        ...


class _TracerProtocol(Protocol):
    """Protocol for the OpenTelemetry tracer used by the SDK."""

    def start_as_current_span(self, name: str) -> AbstractContextManager[_SpanProtocol]:
        """Create a context manager that activates a span."""
        ...

_tracer = None
_meter = None
_histograms: dict[str, _HistogramProtocol] = {}
_histograms_lock = threading.Lock()


def get_tracer() -> _TracerProtocol:
    """Return the SDK OpenTelemetry tracer singleton."""
    global _tracer
    if _tracer is None:
        _tracer = trace.get_tracer("leap0-sdk-python")
    return cast(_TracerProtocol, _tracer)


def get_meter() -> _MeterProtocol:
    """Return the SDK OpenTelemetry meter singleton."""
    global _meter
    if _meter is None:
        _meter = metrics.get_meter("leap0-sdk-python")
    return cast(_MeterProtocol, _meter)


def clear_cached_otel() -> None:
    """Clear cached tracer, meter, and histogram handles."""
    global _tracer, _meter
    _tracer = None
    _meter = None
    with _histograms_lock:
        _histograms.clear()


def _metric_name(name: str) -> str:
    return name.replace(".", "_").lower()


def _get_histogram(name: str) -> _HistogramProtocol:
    histogram_name = _metric_name(name)
    histogram = _histograms.get(histogram_name)
    if histogram is not None:
        return histogram

    with _histograms_lock:
        histogram = _histograms.get(histogram_name)
        if histogram is None:
            histogram = get_meter().create_histogram(
                f"{histogram_name}_duration",
                description=f"Duration of {name}",
                unit="ms",
            )
            _histograms[histogram_name] = histogram
    return histogram


def with_instrumentation(name: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Instrument a function with OpenTelemetry spans and duration metrics."""
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                tracer = get_tracer()
                histogram = _get_histogram(name)

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

            return cast(Callable[P, R], async_wrapper)

        @functools.wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            tracer = get_tracer()
            histogram = _get_histogram(name)

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

        return cast(Callable[P, R], sync_wrapper)

    return decorator
