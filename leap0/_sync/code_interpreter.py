from __future__ import annotations

from collections.abc import Iterator
from typing import Any, cast

import httpx

from .._internal.types import JsonObject
from ..models.code_interpreter import (
    CodeContext, CodeContextDict, CodeExecutionResult, CodeExecutionResultDict, StreamEvent, StreamEventDict,
)
from ..models.errors import Leap0Error
from ..models.sandbox import SandboxRef, sandbox_id_of
from .._utils.errors import intercept_errors
from .._utils.stream import iter_sse_events
from .._utils.url import sandbox_base_url
from ._transport import Transport


class CodeInterpreterClient:
    """Execute code inside a sandbox using a managed interpreter runtime.
    
        Supports Python and TypeScript/JavaScript. Each execution can be linked
        to a persistent context to share state across multiple calls.
    
        Example:
            ```python
            result = client.code_interpreter.execute(
                sandbox,
                code="sum([1, 2, 3])",
                language="python",
            )
            print(result.main_text)
            ```
        
    Attributes:
        None.
    """

    def __init__(self, transport: Transport, *, sandbox_domain: str | None = None):
        self._transport = transport
        self._sandbox_domain = sandbox_domain.strip("/") if sandbox_domain else None

    def _stream_event_from_sse(self, event: object) -> StreamEvent | None:
        if not isinstance(event, dict):
            return None
        if event.get("envelope") == "error":
            message = str(event.get("error") or event.get("message") or "Code execution stream error")
            raise Leap0Error(message, body=str(event))
        return StreamEvent.from_dict(cast(StreamEventDict, event))

    def _request(
        self,
        method: str,
        sandbox: SandboxRef,
        path: str,
        *,
        json: JsonObject | None = None,
        expected_status: int | tuple[int, ...] = 200,
        http_timeout: float | None = None,
    ) -> httpx.Response:
        return self._transport.request_target(
            method,
            f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain)}{path}",
            json=json,
            expected_status=expected_status,
            timeout=http_timeout,
        )

    def _request_json(
        self,
        method: str,
        sandbox: SandboxRef,
        path: str,
        *,
        json: JsonObject | None = None,
        expected_status: int | tuple[int, ...] = 200,
        http_timeout: float | None = None,
    ) -> JsonObject:
        return self._transport.request_target_json(
            method,
            f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain)}{path}",
            json=json,
            expected_status=expected_status,
            timeout=http_timeout,
        )

    @intercept_errors("Failed to check interpreter health: ")
    def health(self, sandbox: SandboxRef, http_timeout: float | None = None) -> bool:
        """Check whether the code interpreter is healthy.

        Args:
            sandbox: Sandbox ID or object.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            bool: ``True`` when the service reports ``"ok"``.
        """
        data = self._request_json("GET", sandbox, "/healthz", http_timeout=http_timeout)
        return data.get("status") == "ok"

    @intercept_errors("Failed to create execution context: ")
    def create_context(self, sandbox: SandboxRef, *, language: str = "python", cwd: str | None = None, http_timeout: float | None = None) -> CodeContext:
        """Create a new execution context.

        Args:
            sandbox: Sandbox ID or object.
            language: Language runtime (default ``"python"``).
            cwd: Working directory for the new context.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            CodeContext: Newly created persistent execution context.
        """
        payload: JsonObject = {"language": language}
        if cwd is not None:
            payload["cwd"] = cwd
        data = cast(CodeContextDict, self._request_json("POST", sandbox, "/contexts", json=payload, expected_status=201, http_timeout=http_timeout))
        return CodeContext.from_dict(data)

    @intercept_errors("Failed to list execution contexts: ")
    def list_contexts(self, sandbox: SandboxRef, http_timeout: float | None = None) -> list[CodeContext]:
        """List all execution contexts in the sandbox.

        Args:
            sandbox: Sandbox ID or object.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            list[CodeContext]: Active execution contexts.
        """
        raw = self._request_json("GET", sandbox, "/contexts", http_timeout=http_timeout)
        # Server wraps response in {"items": [...]}
        items = cast(list[CodeContextDict], raw.get("items", []))
        return [CodeContext.from_dict(item) for item in items]

    @intercept_errors("Failed to get execution context: ")
    def get_context(self, sandbox: SandboxRef, context_id: str, http_timeout: float | None = None) -> CodeContext:
        """Get a single execution context by ID.

        Args:
            sandbox: Sandbox ID or object.
            context_id: Execution context identifier.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            CodeContext: Matching execution context.
        """
        data = cast(CodeContextDict, self._request_json("GET", sandbox, f"/contexts/{context_id}", http_timeout=http_timeout))
        return CodeContext.from_dict(data)

    @intercept_errors("Failed to delete execution context: ")
    def delete_context(
        self,
        sandbox: SandboxRef,
        context_id: str,
        http_timeout: float | None = None,
    ) -> None:
        """Delete an execution context.

        Args:
            sandbox: Sandbox ID or object.
            context_id: Execution context identifier.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        """
        self._request(
            "DELETE",
            sandbox,
            f"/contexts/{context_id}",
            expected_status=204,
            http_timeout=http_timeout,
        )

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
        http_timeout: float | None = None,
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
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            CodeExecutionResult: Structured execution output, errors, and logs.
        """
        payload: JsonObject = {"code": code, "language": language}
        if context_id is not None:
            payload["context_id"] = context_id
        if env_vars is not None:
            payload["env_vars"] = env_vars
        if timeout_ms is not None:
            payload["timeout_ms"] = timeout_ms
        response = self._request("POST", sandbox, "/execute", json=payload, http_timeout=http_timeout)
        data = cast(CodeExecutionResultDict, response.json())
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
        http_timeout: float | None = None,
    ) -> Iterator[StreamEvent]:
        """Execute code and stream output events via SSE.
        
                Yields :class:`StreamEvent` objects with type ``"stdout"``,
                ``"stderr"``, ``"exit"``, or ``"error"``.
        
        Args:
            sandbox: Sandbox ID or object.
            code: Source code to execute.
            language: Language runtime for the operation.
            context_id: Parameter for this operation.
            timeout_ms: Execution timeout in milliseconds.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Yields:
            object: Items yielded by this operation.
        """
        payload: JsonObject = {"code": code, "language": language}
        if context_id is not None:
            payload["context_id"] = context_id
        if timeout_ms is not None:
            payload["timeout_ms"] = timeout_ms
        response = self._transport.stream(
            "POST",
            f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain)}/execute/async",
            json=payload,
            timeout=http_timeout,
        )
        try:
            for event in iter_sse_events(response.iter_lines()):
                stream_event = self._stream_event_from_sse(event)
                if stream_event is not None:
                    yield stream_event
        finally:
            response.close()
