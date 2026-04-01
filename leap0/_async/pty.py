from __future__ import annotations

from urllib.parse import quote
from typing import Any, cast

from websockets.asyncio.client import ClientConnection, connect

from .._internal.types import JsonObject
from ._transport import AsyncTransport
from .._utils.errors import intercept_errors
from .._utils.url import websocket_url_from_http
from ..models.pty import CreatePtySessionParams, PtySession
from .._schemas.pty import PtyListResponseDict, PtySessionInfoDict
from ..models.sandbox import SandboxRef, sandbox_id_of


class AsyncPtyConnection:
    """Asynchronous PTY websocket connection wrapper.
    
    Attributes:
        websocket: Public attribute exposed by this object.
    """
    def __init__(self, websocket: ClientConnection):
        self.websocket = websocket

    async def send(self, data: str | bytes) -> None:
        """Send data through the PTY websocket connection.
        
        Args:
            data: Parameter for this operation.
        """
        payload = data.encode() if isinstance(data, str) else data
        await self.websocket.send(payload)

    async def recv(self) -> bytes:
        """Receive data from the PTY websocket connection.
        
        Returns:
            object: Result returned by this operation.
        """
        message = await self.websocket.recv()
        if isinstance(message, str):
            return message.encode()
        if isinstance(message, bytes):
            return message
        raise TypeError(f"Unexpected message type from websocket: {type(message).__name__}")

    async def close(self) -> None:
        """Close the client and release resources."""
        await self.websocket.close()


class AsyncPtyClient:
    """Create and connect to PTY sessions asynchronously.
    
    Attributes:
        None.
    """
    def __init__(self, transport: AsyncTransport):
        self._transport = transport

    @intercept_errors("Failed to list PTY sessions: ")
    async def list(self, sandbox: SandboxRef) -> list[PtySession]:
        """List PTY sessions for a sandbox.
        
        Args:
            sandbox: Sandbox ID or object.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(PtyListResponseDict, await self._transport.request_json("GET", f"/v1/sandbox/{sandbox_id_of(sandbox)}/pty"))
        return [PtySession.from_dict(item) for item in data.get("items", [])]

    @intercept_errors("Failed to create PTY session: ")
    async def create(
        self,
        sandbox: SandboxRef,
        *,
        session_id: str | None = None,
        cols: int | None = None,
        rows: int | None = None,
        cwd: str | None = None,
        envs: dict[str, str] | None = None,
        lazy_start: bool | None = None,
        http_timeout: float | None = None,
    ) -> PtySession:
        """Create a terminal session with a shell process.

        Args:
            sandbox: Sandbox ID or object.
            session_id: Session ID. Auto-generated if omitted.
            cols: Terminal columns.
            rows: Terminal rows.
            cwd: Starting directory.
            envs: Environment variables.
            lazy_start: Defer shell start until the first WebSocket connection.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            PtySession: Metadata for the created PTY session.
        """
        payload = CreatePtySessionParams(
            session_id=session_id,
            cols=cols,
            rows=rows,
            cwd=cwd,
            envs=envs,
            lazy_start=lazy_start,
        ).to_payload()
        data = cast(PtySessionInfoDict, await self._transport.request_json(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/pty",
            json=payload,
            expected_status=201,
            timeout=http_timeout,
        ))
        return PtySession.from_dict(data)

    @intercept_errors("Failed to get PTY session: ")
    async def get(self, sandbox: SandboxRef, session_id: str) -> PtySession:
        """Get an object by ID or identifier.
        
        Args:
            sandbox: Sandbox ID or object.
            session_id: PTY session identifier.
        
        Returns:
            object: Result returned by this operation.
        """
        encoded_session_id = quote(session_id, safe="")
        data = cast(PtySessionInfoDict, await self._transport.request_json("GET", f"/v1/sandbox/{sandbox_id_of(sandbox)}/pty/{encoded_session_id}"))
        return PtySession.from_dict(data)

    @intercept_errors("Failed to delete PTY session: ")
    async def delete(self, sandbox: SandboxRef, session_id: str, http_timeout: float | None = None) -> None:
        """Kill the shell process and remove the session.
        
        Args:
            sandbox: Sandbox ID or object.
            session_id: PTY session identifier.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        """
        encoded_session_id = quote(session_id, safe="")
        await self._transport.request("DELETE", f"/v1/sandbox/{sandbox_id_of(sandbox)}/pty/{encoded_session_id}", expected_status=204, timeout=http_timeout)

    @intercept_errors("Failed to resize PTY session: ")
    async def resize(self, sandbox: SandboxRef, session_id: str, *, cols: int, rows: int) -> PtySession:
        """Resize a PTY session.
        
        Args:
            sandbox: Sandbox ID or object.
            session_id: PTY session identifier.
            cols: Parameter for this operation.
            rows: Parameter for this operation.
        
        Returns:
            object: Result returned by this operation.
        """
        payload = CreatePtySessionParams(cols=cols, rows=rows).to_payload()
        encoded_session_id = quote(session_id, safe="")
        data = cast(PtySessionInfoDict, await self._transport.request_json(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/pty/{encoded_session_id}/resize",
            json=payload,
        ))
        return PtySession.from_dict(data)

    def websocket_url(self, sandbox: SandboxRef, session_id: str) -> str:
        """Build a websocket URL for this sandbox.
        
        Args:
            sandbox: Sandbox ID or object.
            session_id: PTY session identifier.
        
        Returns:
            object: Result returned by this operation.
        """
        encoded_session_id = quote(session_id, safe="")
        return websocket_url_from_http(f"{self._transport.base_url}/v1/sandbox/{sandbox_id_of(sandbox)}/pty/{encoded_session_id}/connect")

    @intercept_errors("Failed to connect to PTY session: ")
    async def connect(self, sandbox: SandboxRef, session_id: str, http_timeout: float | None = None, **kwargs: Any) -> AsyncPtyConnection:
        """Open a WebSocket connection for interactive terminal I/O.

        Important:
            Callers are responsible for closing the returned connection, ideally
            with ``try/finally`` or an async context manager wrapper.

        Args:
            sandbox: Sandbox ID or object.
            session_id: PTY session identifier.
            http_timeout: Optional WebSocket open timeout in seconds.
            **kwargs: Additional keyword arguments passed to ``websockets.asyncio.client.connect``.

        Returns:
            AsyncPtyConnection: Open WebSocket-backed PTY connection.
        """
        url = self.websocket_url(sandbox, session_id)
        if http_timeout is not None and "open_timeout" not in kwargs:
            kwargs["open_timeout"] = http_timeout
        additional_headers = dict(kwargs.pop("additional_headers", {}) or {})
        additional_headers[self._transport.auth_header] = self._transport.auth_value
        websocket = await connect(url, additional_headers=additional_headers, **kwargs)
        return AsyncPtyConnection(websocket)


__all__ = ["AsyncPtyClient", "AsyncPtyConnection"]
