from __future__ import annotations

from typing import Any

from ._transport import Transport
from ._types import ProcessResultDict
from .models import ProcessResult, SandboxRef, sandbox_id_of


class ProcessClient:
    """Execute one-shot shell commands inside a running sandbox."""

    def __init__(self, transport: Transport):
        self._transport = transport

    def execute(self, sandbox: SandboxRef, *, command: str, cwd: str | None = None, timeout: int | None = None) -> ProcessResult:
        """Run a shell command and wait for the result.

        The command runs inside ``/bin/sh -c``.

        Args:
            sandbox: Sandbox ID or object.
            command: Shell command to execute.
            cwd: Working directory.
            timeout: Timeout in seconds (default 30).
        """
        payload: dict[str, Any] = {"command": command}
        if cwd is not None:
            payload["cwd"] = cwd
        if timeout is not None:
            payload["timeout"] = timeout
        data: ProcessResultDict = self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/process/execute", json=payload)  # type: ignore[assignment]
        return ProcessResult.from_dict(data)
