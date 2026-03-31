from __future__ import annotations

import os
from types import TracebackType
from typing import Self

from ._transport import Transport
from .code_interpreter import CodeInterpreterClient
from .desktop import DesktopClient
from .config import DEFAULT_CLIENT_TIMEOUT, Leap0Config
from .constants import (
    DEFAULT_BASE_URL,
    DEFAULT_DESKTOP_TEMPLATE_NAME,
    DEFAULT_MEMORY_MIB,
    DEFAULT_SANDBOX_DOMAIN,
    DEFAULT_TEMPLATE_NAME,
    DEFAULT_TIMEOUT_MIN,
    DEFAULT_VCPU,
)
from .filesystem import FilesystemClient
from .git import GitClient
from .lsp import LspClient
from .process import ProcessClient
from .pty import PtyClient
from .sandboxes import SandboxesClient
from .ssh import SshClient
from .snapshots import SnapshotsClient
from .templates import TemplatesClient


class Leap0Client:
    """Top-level client for the Leap0 API.

    Provides access to all service clients (sandboxes, snapshots, templates,
    filesystem, git, process, pty, lsp, ssh, code_interpreter,
    desktop).  Can be used as a context manager to ensure the underlying HTTP
    connection is closed on exit.

    Args:
        api_key: API key for authentication. Falls back to the ``LEAP0_API_KEY``
            environment variable when not provided.
        base_url: Base URL of the Leap0 control-plane API. Falls back to the
            ``LEAP0_BASE_URL`` environment variable, then to
            ``https://api.leap0.dev``.
        sandbox_domain: Domain suffix used to build per-sandbox URLs.  Falls
            back to the ``LEAP0_SANDBOX_DOMAIN`` environment variable, then to
            ``sandbox.leap0.dev``.
        timeout: Default HTTP timeout in seconds.
        auth_header: Name of the header used to send the API key.
        bearer: When True, the key is sent with a ``Bearer`` prefix.
    """
    DEFAULT_BASE_URL = DEFAULT_BASE_URL
    DEFAULT_SANDBOX_DOMAIN = DEFAULT_SANDBOX_DOMAIN
    DEFAULT_TEMPLATE_NAME = DEFAULT_TEMPLATE_NAME
    DEFAULT_DESKTOP_TEMPLATE_NAME = DEFAULT_DESKTOP_TEMPLATE_NAME
    DEFAULT_VCPU = DEFAULT_VCPU
    DEFAULT_MEMORY_MIB = DEFAULT_MEMORY_MIB
    DEFAULT_TIMEOUT_MIN = DEFAULT_TIMEOUT_MIN

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        sandbox_domain: str | None = None,
        timeout: float = DEFAULT_CLIENT_TIMEOUT,
        auth_header: str = "authorization",
        bearer: bool = True,
    ):
        resolved_api_key = api_key or os.environ.get("LEAP0_API_KEY")
        if not resolved_api_key:
            raise ValueError("api_key is required or set LEAP0_API_KEY")
        resolved_base_url = base_url or os.environ.get("LEAP0_BASE_URL") or DEFAULT_BASE_URL
        resolved_sandbox_domain = sandbox_domain or os.environ.get("LEAP0_SANDBOX_DOMAIN") or DEFAULT_SANDBOX_DOMAIN
        self._transport = Transport(
            api_key=resolved_api_key,
            base_url=resolved_base_url,
            timeout=timeout,
            auth_header=auth_header,
            bearer=bearer,
        )
        self.sandboxes = SandboxesClient(self._transport, sandbox_domain=resolved_sandbox_domain)
        self.snapshots = SnapshotsClient(self._transport)
        self.templates = TemplatesClient(self._transport)
        self.filesystem = FilesystemClient(self._transport)
        self.git = GitClient(self._transport)
        self.process = ProcessClient(self._transport)
        self.pty = PtyClient(self._transport)
        self.lsp = LspClient(self._transport)
        self.ssh = SshClient(self._transport)
        self.code_interpreter = CodeInterpreterClient(self._transport, sandbox_domain=resolved_sandbox_domain)
        self.desktop = DesktopClient(self._transport, sandbox_domain=resolved_sandbox_domain)

    def close(self) -> None:
        self._transport.close()

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
    """Create a :class:`Leap0Client` from a :class:`Leap0Config`."""
    return Leap0Client(
        api_key=config.api_key,
        base_url=config.base_url,
        sandbox_domain=config.sandbox_domain,
        timeout=config.timeout,
        auth_header=config.auth_header,
        bearer=config.bearer,
    )
