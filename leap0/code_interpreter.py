from __future__ import annotations

from collections.abc import Iterator
from typing import Any, cast

import httpx

from ._transport import Transport
from ._utils.errors import intercept_errors
from ._utils.stream import iter_sse_events
from ._utils.url import sandbox_base_url
from .common.code_interpreter import (
    CodeContext, CodeContextDict, CodeExecutionResult, CodeExecutionResultDict, StreamEvent, StreamEventDict,
)
from .common.sandbox import SandboxRef, sandbox_id_of


class CodeInterpreterClient:
    """Execute code inside a sandbox using a managed interpreter runtime.

    Supports Python and TypeScript/JavaScript. Each execution can be linked
    to a persistent context to share state across multiple calls.
    """

    def __init__(self, transport: Transport, *, sandbox_domain: str | None = None):
        self._transport = transport
        self._sandbox_domain = sandbox_domain.strip("/") if sandbox_domain else None

    def _request(
        self,
        method: str,
        sandbox: SandboxRef,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        expected_status: int | tuple[int, ...] = 200,
    ) -> httpx.Response:
        return self._transport.request_target(
            method,
            f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain)}{path}",
            json=json,
            expected_status=expected_status,
        )

    def _request_json(
        self,
        method: str,
        sandbox: SandboxRef,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        expected_status: int | tuple[int, ...] = 200,
    ) -> dict[str, Any]:
        return self._transport.request_target_json(
            method,
            f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain)}{path}",
            json=json,
            expected_status=expected_status,
        )

    @intercept_errors("Failed to check interpreter health: ")
    def health(self, sandbox: SandboxRef) -> bool:
        """Check if the code interpreter is healthy. Returns True if status is ok."""
        data = self._request_json("GET", sandbox, "/healthz")
        return data.get("status") == "ok"

    @intercept_errors("Failed to create execution context: ")
    def create_context(self, sandbox: SandboxRef, *, language: str = "python", cwd: str | None = None) -> CodeContext:
        """Create a new execution context.

        Args:
            sandbox: Sandbox ID or object.
            language: Language runtime (e.g. ``"python"``, ``"typescript"``).
            cwd: Working directory (default ``"/home/user"``).
        """
        payload: dict[str, Any] = {"language": language}
        if cwd is not None:
            payload["cwd"] = cwd
        data: CodeContextDict = self._request_json("POST", sandbox, "/contexts", json=payload, expected_status=201)  # type: ignore[assignment]
        return CodeContext.from_dict(data)

    @intercept_errors("Failed to list execution contexts: ")
    def list_contexts(self, sandbox: SandboxRef) -> list[CodeContext]:
        """List all execution contexts in the sandbox."""
        raw = self._request_json("GET", sandbox, "/contexts")
        # Server wraps response in {"items": [...]}
        items: list[CodeContextDict] = raw.get("items", [])  # type: ignore[assignment]
        return [CodeContext.from_dict(item) for item in items]

    @intercept_errors("Failed to get execution context: ")
    def get_context(self, sandbox: SandboxRef, context_id: str) -> CodeContext:
        """Get a single execution context by ID."""
        data: CodeContextDict = self._request_json("GET", sandbox, f"/contexts/{context_id}")  # type: ignore[assignment]
        return CodeContext.from_dict(data)

    @intercept_errors("Failed to delete execution context: ")
    def delete_context(self, sandbox: SandboxRef, context_id: str) -> None:
        """Delete an execution context."""
        self._request("DELETE", sandbox, f"/contexts/{context_id}", expected_status=204)

    @intercept_errors("Failed to execute code: ")
    def execute(
        self,
        sandbox: SandboxRef,
        *,
        code: str,
        language: str = "python",
        context_id: str | None = None,
        env_vars: dict[str, str] | None = None,
        timeout_ms: int | None = None,
    ) -> CodeExecutionResult:
        """Execute code and wait for the full result.

        Args:
            sandbox: Sandbox ID or object.
            code: Source code to execute.
            language: Language runtime (default ``"python"``).
            context_id: Link to an existing context to share state.
                Auto-generated if omitted.
            env_vars: Environment variables for the execution.
            timeout_ms: Execution timeout in milliseconds (default 30000).
        """
        payload: dict[str, Any] = {"code": code, "language": language}
        if context_id is not None:
            payload["context_id"] = context_id
        if env_vars is not None:
            payload["env_vars"] = env_vars
        if timeout_ms is not None:
            payload["timeout_ms"] = timeout_ms
        response = self._request("POST", sandbox, "/execute", json=payload)
        data: CodeExecutionResultDict = response.json()  # type: ignore[assignment]
        return CodeExecutionResult.from_dict(data)

    @intercept_errors("Failed to execute code: ")
    def execute_stream(
        self,
        sandbox: SandboxRef,
        *,
        code: str,
        language: str = "python",
        context_id: str | None = None,
        timeout_ms: int | None = None,
    ) -> Iterator[StreamEvent]:
        """Execute code and stream output events via SSE.

        Yields :class:`StreamEvent` objects with type ``"stdout"``,
        ``"stderr"``, ``"exit"``, or ``"error"``.

        Args:
            sandbox: Sandbox ID or object.
            code: Source code to execute.
            language: Language runtime (default ``"python"``).
            context_id: Link to an existing context to share state.
            timeout_ms: Execution timeout in milliseconds (default 30000).
        """
        payload: dict[str, Any] = {"code": code, "language": language}
        if context_id is not None:
            payload["context_id"] = context_id
        if timeout_ms is not None:
            payload["timeout_ms"] = timeout_ms
        response = self._transport.stream(
            "POST",
            f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain)}/execute/async",
            json=payload,
        )
        try:
            for event in iter_sse_events(response.iter_lines()):
                yield StreamEvent.from_dict(cast(StreamEventDict, event))
        finally:
            response.close()
