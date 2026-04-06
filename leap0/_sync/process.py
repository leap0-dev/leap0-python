from __future__ import annotations

from typing import cast

from .._internal.types import JsonObject
from ..models.process import ProcessResult
from ..models.sandbox import SandboxRef, sandbox_id_of
from .._schemas.process import ProcessResultDict
from .._utils.errors import intercept_errors
from ._transport import Transport


class ProcessClient:
    """Execute one-shot shell commands inside a running sandbox.
    
        Use this client for non-interactive command execution where you want the
        full result back as a single response.
        
    Attributes:
        None.
    """

    def __init__(self, transport: Transport):
        self._transport = transport

    @intercept_errors("Failed to execute command: ")
    def execute(self, sandbox: SandboxRef, *, command: str, cwd: str | None = None, timeout: int | None = None, http_timeout: int | None = None) -> ProcessResult:
        """Run a shell command and wait for the result.

        The command runs inside ``/bin/sh -c``.

        Args:
            sandbox: Sandbox ID or object.
            command: Shell command to execute.
            cwd: Working directory.
            timeout: Timeout in seconds. If omitted, the server-side default is used.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            ProcessResult: Command result including exit code, stdout, and stderr.

        Example:
            ```python
            result = sandbox.process.execute(
                command="ls -la /workspace",
            )
            print(result.stdout)
            print(result.stderr)
            ```
        """
        payload: JsonObject = {"command": command}
        if cwd is not None:
            payload["cwd"] = cwd
        if timeout is not None:
            payload["timeout"] = timeout
        data = cast(ProcessResultDict, self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/process/execute", json=payload, timeout=http_timeout))
        return ProcessResult.from_dict(data)
