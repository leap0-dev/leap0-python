from __future__ import annotations

from typing import Any, cast

from websockets.sync.client import connect

from .._internal.types import JsonObject
from ._transport import Transport
from .._utils.errors import intercept_errors
from .._utils.url import websocket_url_from_http
from ..models.pty import CreatePtySessionParams, PtyConnection, PtySession
from .._schemas.pty import PtyListResponseDict, PtySessionInfoDict
from ..models.sandbox import SandboxRef, sandbox_id_of


class PtyClient:
    """Create and manage interactive terminal sessions inside a sandbox.
    
        Connect via WebSocket for real-time bidirectional I/O, similar to SSH or
        a browser-based terminal.
    
        Example:
            ```python
            sandbox = client.sandboxes.create()
            session = sandbox.pty.create(cols=120, rows=30)
            conn = sandbox.pty.connect(session.id)
            conn.send("pwd
    ")
            print(conn.recv().decode())
            conn.close()
            ```
        
    Attributes:
        None.
    """

    def __init__(self, transport: Transport):
        self._transport = transport

    @intercept_errors("Failed to list PTY sessions: ")
    def list(self, sandbox: SandboxRef) -> list[PtySession]:
        """List all PTY sessions for a sandbox.
        
        Args:
            sandbox: Sandbox ID or object.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(PtyListResponseDict, self._transport.request_json("GET", f"/v1/sandbox/{sandbox_id_of(sandbox)}/pty"))
        return [PtySession.from_dict(item) for item in data.get("items", [])]

    @intercept_errors("Failed to create PTY session: ")
    def create(
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

        Args:
            sandbox: Sandbox ID or object.
            session_id: PTY session identifier.
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
        data = cast(PtySessionInfoDict, self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/pty", json=payload, expected_status=201, timeout=http_timeout))
        return PtySession.from_dict(data)

    @intercept_errors("Failed to get PTY session: ")
    def get(self, sandbox: SandboxRef, session_id: str) -> PtySession:
        """Get details for a single PTY session.
        
        Args:
            sandbox: Sandbox ID or object.
            session_id: PTY session identifier.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(PtySessionInfoDict, self._transport.request_json("GET", f"/v1/sandbox/{sandbox_id_of(sandbox)}/pty/{session_id}"))
        return PtySession.from_dict(data)

    @intercept_errors("Failed to delete PTY session: ")
    def delete(self, sandbox: SandboxRef, session_id: str, http_timeout: float | None = None) -> None:
        """Kill the shell process and remove the session.
        
        Args:
            sandbox: Sandbox ID or object.
            session_id: PTY session identifier.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        """
        self._transport.request("DELETE", f"/v1/sandbox/{sandbox_id_of(sandbox)}/pty/{session_id}", expected_status=204, timeout=http_timeout)

    @intercept_errors("Failed to resize PTY session: ")
    def resize(self, sandbox: SandboxRef, session_id: str, *, cols: int, rows: int) -> PtySession:
        """Change the terminal dimensions while connected.
        
        Args:
            sandbox: Sandbox ID or object.
            session_id: PTY session identifier.
            cols: Parameter for this operation.
            rows: Parameter for this operation.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(PtySessionInfoDict, self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/pty/{session_id}/resize", json={"cols": cols, "rows": rows}))
        return PtySession.from_dict(data)

    def websocket_url(self, sandbox: SandboxRef, session_id: str) -> str:
        """Build the WSS URL for connecting to a PTY session.
        
        Args:
            sandbox: Sandbox ID or object.
            session_id: PTY session identifier.
        
        Returns:
            object: Result returned by this operation.
        """
        return websocket_url_from_http(f"{self._transport.base_url}/v1/sandbox/{sandbox_id_of(sandbox)}/pty/{session_id}/connect")

    @intercept_errors("Failed to connect to PTY session: ")
    def connect(self, sandbox: SandboxRef, session_id: str, http_timeout: float | None = None, **kwargs: Any) -> PtyConnection:
        """Open a WebSocket connection for interactive terminal I/O.

        Returns a :class:`PtyConnection` with ``send``, ``recv``, and
        ``close`` methods. All messages are binary frames containing raw
        terminal bytes.

        Args:
            sandbox: Sandbox ID or object.
            session_id: PTY session identifier.
            http_timeout: Optional WebSocket open timeout in seconds.
            **kwargs: Additional keyword arguments passed to ``websockets.sync.client.connect``.

        Returns:
            PtyConnection: Open WebSocket-backed PTY connection.
        """
        url = self.websocket_url(sandbox, session_id)
        if http_timeout is not None and "open_timeout" not in kwargs:
            kwargs["open_timeout"] = http_timeout
        websocket = connect(url, additional_headers={self._transport.auth_header: self._transport.auth_value}, **kwargs)
        return PtyConnection(websocket=websocket)
