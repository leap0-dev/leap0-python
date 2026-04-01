from __future__ import annotations

import asyncio
import threading
from types import TracebackType

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.attributes import service_attributes
from opentelemetry.trace import ProxyTracerProvider

from opentelemetry.metrics import _internal as metrics_internal
from opentelemetry.util._once import Once

from .._internal.version import SDK_VERSION
from .._utils.otel import clear_cached_otel
from ..models.config import (
    DEFAULT_BASE_URL,
    DEFAULT_CLIENT_TIMEOUT,
    DEFAULT_CODE_INTERPRETER_TEMPLATE_NAME,
    DEFAULT_DESKTOP_TEMPLATE_NAME,
    DEFAULT_MEMORY_MIB,
    DEFAULT_SANDBOX_DOMAIN,
    DEFAULT_TEMPLATE_NAME,
    DEFAULT_TIMEOUT_MIN,
    DEFAULT_VCPU,
    Leap0Config,
)
from .._utils.otel import with_instrumentation
from ._transport import AsyncTransport
from .code_interpreter import AsyncCodeInterpreterClient
from .desktop import AsyncDesktopClient
from .filesystem import AsyncFilesystemClient
from .git import AsyncGitClient
from .lsp import AsyncLspClient
from .process import AsyncProcessClient
from .pty import AsyncPtyClient, AsyncPtyConnection
from .sandbox import AsyncSandbox, AsyncSandboxesClient
from .snapshots import AsyncSnapshotsClient
from .ssh import AsyncSshClient
from .templates import AsyncTemplatesClient


_otel_lock = threading.Lock()
_shared_tracer_provider: TracerProvider | None = None
_shared_tracer_refcount = 0
_shared_meter_provider: MeterProvider | None = None
_shared_meter_refcount = 0


def _reset_tracer_provider_if_current(provider: TracerProvider) -> None:
    if trace.get_tracer_provider() is not provider:
        return
    trace._TRACER_PROVIDER = ProxyTracerProvider()  # type: ignore[attr-defined]
    trace._TRACER_PROVIDER_SET_ONCE = Once()  # type: ignore[attr-defined]


def _reset_meter_provider_if_current(provider: MeterProvider) -> None:
    if metrics.get_meter_provider() is not provider:
        return
    metrics_internal._METER_PROVIDER = metrics_internal._PROXY_METER_PROVIDER  # type: ignore[attr-defined]
    metrics_internal._METER_PROVIDER_SET_ONCE = Once()  # type: ignore[attr-defined]


class AsyncLeap0Client:
    """Top-level asynchronous client for the Leap0 API.

    Use this client to create sandboxes and access all async service clients.

    Attributes:
        sandboxes: Client for sandbox lifecycle operations.
        snapshots: Client for snapshot lifecycle operations.
        templates: Client for template management.
        filesystem: Client for sandbox filesystem operations.
        git: Client for Git operations inside a sandbox.
        process: Client for one-shot process execution.
        pty: Client for interactive PTY sessions.
        lsp: Client for Language Server Protocol operations.
        ssh: Client for SSH credential management.
        code_interpreter: Client for code execution APIs.
        desktop: Client for desktop automation APIs.
    """
    DEFAULT_BASE_URL = DEFAULT_BASE_URL
    DEFAULT_SANDBOX_DOMAIN = DEFAULT_SANDBOX_DOMAIN
    DEFAULT_TEMPLATE_NAME = DEFAULT_TEMPLATE_NAME
    DEFAULT_CODE_INTERPRETER_TEMPLATE_NAME = DEFAULT_CODE_INTERPRETER_TEMPLATE_NAME
    DEFAULT_DESKTOP_TEMPLATE_NAME = DEFAULT_DESKTOP_TEMPLATE_NAME
    DEFAULT_VCPU = DEFAULT_VCPU
    DEFAULT_MEMORY_MIB = DEFAULT_MEMORY_MIB
    DEFAULT_TIMEOUT_MIN = DEFAULT_TIMEOUT_MIN

    _tracer_provider: TracerProvider | None = None
    _meter_provider: MeterProvider | None = None

    def __init__(
        self,
        *,
        config: Leap0Config | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        sandbox_domain: str | None = None,
        timeout: float = DEFAULT_CLIENT_TIMEOUT,
        auth_header: str = "authorization",
        bearer: bool = True,
        otel_enabled: bool | None = None,
    ):
        if config is not None:
            provided_overrides = {
                "api_key": api_key,
                "base_url": base_url,
                "sandbox_domain": sandbox_domain,
                "auth_header": auth_header if auth_header != "authorization" else None,
                "bearer": bearer if bearer is not True else None,
                "otel_enabled": otel_enabled,
            }
            if timeout != DEFAULT_CLIENT_TIMEOUT:
                provided_overrides["timeout"] = timeout
            conflicting = [name for name, value in provided_overrides.items() if value is not None]
            if conflicting:
                joined = ", ".join(conflicting)
                raise ValueError(f"Cannot pass config with individual overrides: {joined}")
        if config is None:
            config = Leap0Config(
                api_key=api_key,
                base_url=base_url,
                sandbox_domain=sandbox_domain,
                timeout=timeout,
                auth_header=auth_header,
                bearer=bearer,
                otel_enabled=otel_enabled,
            )
        self._transport = AsyncTransport(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
            auth_header=config.auth_header,
            bearer=config.bearer,
        )
        self._uses_shared_tracer_provider = False
        self._uses_shared_meter_provider = False
        self._closed = False
        self.sandboxes: AsyncSandboxesClient[AsyncSandbox] = AsyncSandboxesClient(
            self._transport,
            sandbox_domain=config.sandbox_domain,
            sandbox_factory=lambda data: AsyncSandbox(self, data),
        )
        self.snapshots: AsyncSnapshotsClient[AsyncSandbox] = AsyncSnapshotsClient(
            self._transport,
            sandbox_factory=lambda data: AsyncSandbox(self, data),
        )
        self.templates = AsyncTemplatesClient(self._transport)
        self.filesystem = AsyncFilesystemClient(self._transport)
        self.git = AsyncGitClient(self._transport)
        self.process = AsyncProcessClient(self._transport)
        self.pty = AsyncPtyClient(self._transport)
        self.lsp = AsyncLspClient(self._transport)
        self.ssh = AsyncSshClient(self._transport)
        self.code_interpreter = AsyncCodeInterpreterClient(self._transport, sandbox_domain=config.sandbox_domain)
        self.desktop = AsyncDesktopClient(self._transport, sandbox_domain=config.sandbox_domain)

        if config.otel_enabled:
            self._init_otel()

    def _init_otel(self) -> None:
        resource = Resource.create(
            {
                service_attributes.SERVICE_NAME: "leap0-python-sdk",
                service_attributes.SERVICE_VERSION: SDK_VERSION,
            }
        )
        self._uses_shared_tracer_provider = False
        self._uses_shared_meter_provider = False

        global _shared_tracer_provider, _shared_tracer_refcount
        current_tracer_provider = trace.get_tracer_provider()
        with _otel_lock:
            if _shared_tracer_provider is None and isinstance(current_tracer_provider, TracerProvider):
                self._tracer_provider = current_tracer_provider
            else:
                if _shared_tracer_provider is None:
                    tracer_provider = TracerProvider(resource=resource)
                    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
                    _shared_tracer_provider = tracer_provider
                    trace.set_tracer_provider(tracer_provider)
                    clear_cached_otel()
                _shared_tracer_refcount += 1
                self._tracer_provider = _shared_tracer_provider
                self._uses_shared_tracer_provider = True

        global _shared_meter_provider, _shared_meter_refcount
        current_meter_provider = metrics.get_meter_provider()
        with _otel_lock:
            if _shared_meter_provider is None and isinstance(current_meter_provider, MeterProvider):
                self._meter_provider = current_meter_provider
            else:
                if _shared_meter_provider is None:
                    metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
                    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
                    _shared_meter_provider = meter_provider
                    metrics.set_meter_provider(meter_provider)
                    clear_cached_otel()
                _shared_meter_refcount += 1
                self._meter_provider = _shared_meter_provider
                self._uses_shared_meter_provider = True

    @with_instrumentation("async_client.get_sandbox")
    async def get_sandbox(self, sandbox_id: str) -> AsyncSandbox:
        """Get a sandbox by ID.

        Args:
            sandbox_id: Sandbox identifier.

        Returns:
            AsyncSandbox: Sandbox object with bound service clients.
        """
        return await self.sandboxes.get(sandbox_id)

    @with_instrumentation("async_client.create_sandbox")
    async def create_sandbox(self, **kwargs: object) -> AsyncSandbox:
        """Create a sandbox.

        Args:
            **kwargs: Keyword arguments forwarded to ``client.sandboxes.create``.

        Returns:
            AsyncSandbox: Sandbox object with bound service clients.
        """
        return await self.sandboxes.create(**kwargs)

    @with_instrumentation("async_client.close")
    async def close(self) -> None:
        """Close the client and release resources."""
        if self._closed:
            return
        self._closed = True
        await self._transport.close()

        tracer_to_shutdown: TracerProvider | None = None
        meter_to_shutdown: MeterProvider | None = None

        global _shared_tracer_provider, _shared_tracer_refcount
        global _shared_meter_provider, _shared_meter_refcount
        with _otel_lock:
            if self._uses_shared_tracer_provider and self._tracer_provider is _shared_tracer_provider:
                _shared_tracer_refcount -= 1
                if _shared_tracer_refcount == 0 and _shared_tracer_provider is not None:
                    tracer_to_shutdown = _shared_tracer_provider
                    _reset_tracer_provider_if_current(_shared_tracer_provider)
                    _shared_tracer_provider = None
                    clear_cached_otel()
            if self._uses_shared_meter_provider and self._meter_provider is _shared_meter_provider:
                _shared_meter_refcount -= 1
                if _shared_meter_refcount == 0 and _shared_meter_provider is not None:
                    meter_to_shutdown = _shared_meter_provider
                    _reset_meter_provider_if_current(_shared_meter_provider)
                    _shared_meter_provider = None
                    clear_cached_otel()

        if tracer_to_shutdown is not None:
            await asyncio.to_thread(tracer_to_shutdown.shutdown)
        if meter_to_shutdown is not None:
            await asyncio.to_thread(meter_to_shutdown.shutdown)

    async def __aenter__(self) -> AsyncLeap0Client:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.close()


def AsyncLeap0(config: Leap0Config) -> AsyncLeap0Client:
    """Create an asynchronous Leap0 client from a config object.

    Args:
        config: Fully resolved Leap0 client configuration.

    Returns:
        AsyncLeap0Client: Configured asynchronous client instance.
    """
    return AsyncLeap0Client(config=config)


__all__ = ["AsyncLeap0", "AsyncLeap0Client", "AsyncPtyConnection"]
