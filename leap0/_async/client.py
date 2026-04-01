from __future__ import annotations

from types import TracebackType

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.attributes import service_attributes

from ._transport import AsyncTransport
from .._internal.version import SDK_VERSION
from .._utils.otel import with_instrumentation
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
        api_key: str | None = None,
        base_url: str | None = None,
        sandbox_domain: str | None = None,
        timeout: float = DEFAULT_CLIENT_TIMEOUT,
        auth_header: str = "authorization",
        bearer: bool = True,
        otel_enabled: bool | None = None,
    ):
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
        self._owns_tracer_provider = False
        self._owns_meter_provider = False
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
        self._owns_tracer_provider = False
        self._owns_meter_provider = False
        resource = Resource.create(
            {
                service_attributes.SERVICE_NAME: "leap0-python-sdk",
                service_attributes.SERVICE_VERSION: SDK_VERSION,
            }
        )
        current_tracer_provider = trace.get_tracer_provider()
        if not isinstance(current_tracer_provider, TracerProvider):
            self._tracer_provider = TracerProvider(resource=resource)
            self._tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
            trace.set_tracer_provider(self._tracer_provider)
            self._owns_tracer_provider = True
        else:
            self._tracer_provider = current_tracer_provider

        current_meter_provider = metrics.get_meter_provider()
        if not isinstance(current_meter_provider, MeterProvider):
            self._meter_provider = MeterProvider(resource=resource)
            metrics.set_meter_provider(self._meter_provider)
            self._owns_meter_provider = True
        else:
            self._meter_provider = current_meter_provider

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
        await self._transport.close()
        if self._owns_tracer_provider and self._tracer_provider is not None:
            self._tracer_provider.shutdown()
        if self._owns_meter_provider and self._meter_provider is not None:
            self._meter_provider.shutdown()

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
    return AsyncLeap0Client(
        api_key=config.api_key,
        base_url=config.base_url,
        sandbox_domain=config.sandbox_domain,
        timeout=config.timeout,
        auth_header=config.auth_header,
        bearer=config.bearer,
        otel_enabled=config.otel_enabled,
    )


__all__ = ["AsyncLeap0", "AsyncLeap0Client", "AsyncPtyConnection"]
