from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, cast

import httpx

from .._internal.types import JsonObject
from ._transport import AsyncTransport
from .._utils.errors import intercept_errors
from .._utils.stream import aiter_sse_events
from .._utils.url import sandbox_base_url
from ..models.code_interpreter import (
    CodeContext,
    CodeContextDict,
    CodeExecutionResult,
    CodeExecutionResultDict,
    StreamEvent,
    StreamEventDict,
)
from ..models.sandbox import SandboxRef, sandbox_id_of


class AsyncCodeInterpreterClient:
    """Execute code inside a sandbox with asynchronous APIs.
    
    Attributes:
        None.
    """
    def __init__(self, transport: AsyncTransport, *, sandbox_domain: str | None = None):
        self._transport = transport
        self._sandbox_domain = sandbox_domain.strip("/") if sandbox_domain else None

    async def _request(
        self,
        method: str,
        sandbox: SandboxRef,
        path: str,
        *,
        json: JsonObject | None = None,
        expected_status: int | tuple[int, ...] = 200,
        http_timeout: float | None = None,
    ) -> httpx.Response:
        return await self._transport.request_target(
            method,
            f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain)}{path}",
            json=json,
            expected_status=expected_status,
            timeout=http_timeout,
        )

    async def _request_json(
        self,
        method: str,
        sandbox: SandboxRef,
        path: str,
        *,
        json: JsonObject | None = None,
        expected_status: int | tuple[int, ...] = 200,
        http_timeout: float | None = None,
    ) -> JsonObject:
        return await self._transport.request_target_json(
            method,
            f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain)}{path}",
            json=json,
            expected_status=expected_status,
            timeout=http_timeout,
        )

    @intercept_errors("Failed to check interpreter health: ")
    async def health(self, sandbox: SandboxRef) -> bool:
        """Check service health.
        
        Args:
            sandbox: Sandbox ID or object.
        
        Returns:
            object: Result returned by this operation.
        """
        data = await self._request_json("GET", sandbox, "/healthz")
        return data.get("status") == "ok"

    @intercept_errors("Failed to create execution context: ")
    async def create_context(self, sandbox: SandboxRef, *, language: str = "python", cwd: str | None = None, http_timeout: float | None = None) -> CodeContext:
        """Create a new execution context.
        
                Args:
                    sandbox: Sandbox ID or object.
                    language: Language runtime (e.g. ``"python"``, ``"typescript"``).
                    cwd: Working directory (default ``"/home/user"``).
        
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Args:
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
                    CodeContext: Newly created persistent execution context.
                
        """
        payload: JsonObject = {"language": language}
        if cwd is not None:
            payload["cwd"] = cwd
        data = cast(CodeContextDict, await self._request_json("POST", sandbox, "/contexts", json=payload, expected_status=201, http_timeout=http_timeout))
        return CodeContext.from_dict(data)

    @intercept_errors("Failed to list execution contexts: ")
    async def list_contexts(self, sandbox: SandboxRef) -> list[CodeContext]:
        """List execution contexts.
        
        Args:
            sandbox: Sandbox ID or object.
        
        Returns:
            object: Result returned by this operation.
        """
        raw = await self._request_json("GET", sandbox, "/contexts")
        items = cast(list[CodeContextDict], raw.get("items", []))
        return [CodeContext.from_dict(item) for item in items]

    @intercept_errors("Failed to get execution context: ")
    async def get_context(self, sandbox: SandboxRef, context_id: str, http_timeout: float | None = None) -> CodeContext:
        """Get a single execution context by ID.
                
                        Returns:
                            CodeContext: Matching execution context.
        
        Args:
            sandbox: Sandbox ID or object.
            context_id: Parameter for this operation.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        """
        data = cast(CodeContextDict, await self._request_json("GET", sandbox, f"/contexts/{context_id}", http_timeout=http_timeout))
        return CodeContext.from_dict(data)

    @intercept_errors("Failed to delete execution context: ")
    async def delete_context(self, sandbox: SandboxRef, context_id: str) -> None:
        """Delete an execution context.
        
        Args:
            sandbox: Sandbox ID or object.
            context_id: Parameter for this operation.
        """
        await self._request("DELETE", sandbox, f"/contexts/{context_id}", expected_status=204)

    @intercept_errors("Failed to execute code: ")
    async def execute(
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

        Args:
                    sandbox: Sandbox ID or object.
                    code: Source code to execute.
                    language: Language runtime (default ``"python"``).
                    context_id: Link to an existing context to share state.
                    timeout_ms: Execution timeout in milliseconds (default 30000).
        
                Yields:
                    StreamEvent: Streaming stdout, stderr, exit, and error events.
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
        response = await self._request("POST", sandbox, "/execute", json=payload, http_timeout=http_timeout)
        data = cast(CodeExecutionResultDict, response.json())
        return CodeExecutionResult.from_dict(data)

    @intercept_errors("Failed to execute code: ")
    async def execute_stream(
        self,
        sandbox: SandboxRef,
        *,
        code: str,
        language: str = "python",
        context_id: str | None = None,
        timeout_ms: int | None = None,
        http_timeout: float | None = None,
    ) -> AsyncIterator[StreamEvent]:
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
        response = await self._transport.stream(
            "POST",
            f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain)}/execute/async",
            json=payload,
            timeout=http_timeout,
        )
        try:
            async for event in aiter_sse_events(response.aiter_lines()):
                yield StreamEvent.from_dict(cast(StreamEventDict, event))
        finally:
            await response.aclose()


__all__ = ["AsyncCodeInterpreterClient"]
