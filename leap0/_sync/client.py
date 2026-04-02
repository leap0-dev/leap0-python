from __future__ import annotations

from types import TracebackType
from typing import Self
import warnings

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.attributes import service_attributes

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
from ._transport import Transport
from .code_interpreter import CodeInterpreterClient
from .desktop import DesktopClient
from .filesystem import FilesystemClient
from .git import GitClient
from .lsp import LspClient
from .process import ProcessClient
from .pty import PtyClient
from .sandbox import Sandbox, SandboxesClient
from .ssh import SshClient
from .snapshots import SnapshotsClient
from .templates import TemplatesClient


class Leap0Client:
    """Top-level client for the Leap0 API.

    Use this client to create sandboxes and access top-level control-plane
    services. Sandbox-scoped services are exposed through bound sandbox objects.
    It can be used directly or as a context manager.

    Args:
        api_key: API key for authentication. Falls back to ``LEAP0_API_KEY``.
        base_url: Control-plane base URL. Falls back to ``LEAP0_BASE_URL``.
        sandbox_domain: Sandbox domain suffix. Falls back to
            ``LEAP0_SANDBOX_DOMAIN``.
        timeout: Default HTTP timeout in seconds.
        auth_header: Header name used to send the API key.
        bearer: Whether to prefix the API key with ``Bearer``.

    Attributes:
        sandboxes: Client for sandbox lifecycle operations.
        snapshots: Client for snapshot lifecycle operations.
        templates: Client for template management.
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
        sdk_otel_enabled: bool | None = None,
    ):
        if otel_enabled is not None:
            warnings.warn(
                "otel_enabled is deprecated; use sdk_otel_enabled instead",
                DeprecationWarning,
                stacklevel=2,
            )
            if sdk_otel_enabled is None:
                sdk_otel_enabled = otel_enabled
        config = Leap0Config(
            api_key=api_key,
            base_url=base_url,
            sandbox_domain=sandbox_domain,
            timeout=timeout,
            auth_header=auth_header,
            bearer=bearer,
            sdk_otel_enabled=sdk_otel_enabled,
        )
        self._transport = Transport(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
            auth_header=config.auth_header,
            bearer=config.bearer,
        )
        self._owns_tracer_provider = False
        self._owns_meter_provider = False
        self.sandboxes: SandboxesClient[Sandbox] = SandboxesClient(
            self._transport,
            sandbox_domain=config.sandbox_domain,
            sandbox_factory=lambda data: Sandbox(self, data),
        )
        self.snapshots: SnapshotsClient[Sandbox] = SnapshotsClient(
            self._transport,
            sandbox_factory=lambda data: Sandbox(self, data),
        )
        self.templates = TemplatesClient(self._transport)
        self._filesystem = FilesystemClient(self._transport)
        self._git = GitClient(self._transport)
        self._process = ProcessClient(self._transport)
        self._pty = PtyClient(self._transport)
        self._lsp = LspClient(self._transport)
        self._ssh = SshClient(self._transport)
        self._code_interpreter = CodeInterpreterClient(self._transport, sandbox_domain=config.sandbox_domain)
        self._desktop = DesktopClient(self._transport, sandbox_domain=config.sandbox_domain)

        if config.sdk_otel_enabled:
            self._init_otel()

    def _init_otel(self) -> None:
        self._owns_tracer_provider = False
        self._owns_meter_provider = False
        resource = Resource.create(
            {
                service_attributes.SERVICE_NAME: "leap0-python-sdk",
                service_attributes.SERVICE_VERSION: self._transport.headers().get("Leap0-SDK-Version", "unknown"),
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
            metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter())
            self._meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
            metrics.set_meter_provider(self._meter_provider)
            self._owns_meter_provider = True
        else:
            self._meter_provider = current_meter_provider

    def __getattr__(self, name: str) -> object:
        if name in {"filesystem", "git", "process", "pty", "lsp", "ssh", "code_interpreter", "desktop"}:
            raise AttributeError(
                f"{type(self).__name__!s} has no attribute {name!r}; use a bound sandbox handle instead, "
                f"for example sandbox.{name}"
            )
        raise AttributeError(f"{type(self).__name__!s} has no attribute {name!r}")

    @with_instrumentation("client.get_sandbox")
    def get_sandbox(self, sandbox_id: str) -> Sandbox:
        """Get a sandbox object with bound service clients by ID.

        Args:
            sandbox_id: Sandbox identifier.

        Returns:
            Sandbox: Sandbox object with bound service clients.
        """
        return self.sandboxes.get(sandbox_id)

    @with_instrumentation("client.create_sandbox")
    def create_sandbox(self, **kwargs: object) -> Sandbox:
        """Create a sandbox and return it as a bound sandbox object.

        Args:
            **kwargs: Keyword arguments forwarded to ``client.sandboxes.create``.

        Returns:
            Sandbox: Sandbox object with bound service clients.
        """
        return self.sandboxes.create(**kwargs)

    @with_instrumentation("client.close")
    def close(self) -> None:
        """Close the underlying HTTP transport.

        Call this when you are done with the client if you are not using a
        context manager.
        """
        self._transport.close()
        if self._owns_tracer_provider and self._tracer_provider is not None:
            self._tracer_provider.shutdown()
        if self._owns_meter_provider and self._meter_provider is not None:
            self._meter_provider.shutdown()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()


def Leap0(config: Leap0Config) -> Leap0Client:
    """Create a synchronous Leap0 client from a config object.

    Args:
        config: Fully resolved Leap0 client configuration.

    Returns:
        Leap0Client: Configured synchronous client instance.
    """
    return Leap0Client(
        api_key=config.api_key,
        base_url=config.base_url,
        sandbox_domain=config.sandbox_domain,
        timeout=config.timeout,
        auth_header=config.auth_header,
        bearer=config.bearer,
        sdk_otel_enabled=config.sdk_otel_enabled,
    )
