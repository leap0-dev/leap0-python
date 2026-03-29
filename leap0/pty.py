from __future__ import annotations

from typing import Any

from websockets.sync.client import connect

from ._transport import Transport
from ._types import PtyListResponseDict, PtySessionInfoDict
from ._utils import websocket_url_from_http
from .exceptions import Leap0WebSocketError
from .models import PtyConnection, PtySession, SandboxRef, sandbox_id_of


class PtyClient:
    """Create and manage interactive terminal sessions inside a sandbox.

    Connect via WebSocket for real-time bidirectional I/O, similar to SSH or
    a browser-based terminal.
    """

    def __init__(self, transport: Transport):
        self._transport = transport

    def list(self, sandbox: SandboxRef) -> list[PtySession]:
        """List all PTY sessions for a sandbox."""
        data: PtyListResponseDict = self._transport.request_json("GET", f"/v1/sandbox/{sandbox_id_of(sandbox)}/pty")  # type: ignore[assignment]
        return [PtySession.from_dict(item) for item in data.get("items", [])]

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
        """
        payload: dict[str, Any] = {}
        if session_id is not None:
            payload["id"] = session_id
        if cols is not None:
            payload["cols"] = cols
        if rows is not None:
            payload["rows"] = rows
        if cwd is not None:
            payload["cwd"] = cwd
        if envs is not None:
            payload["envs"] = envs
        if lazy_start is not None:
            payload["lazy_start"] = lazy_start
        data: PtySessionInfoDict = self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/pty", json=payload, expected_status=201)  # type: ignore[assignment]
        return PtySession.from_dict(data)

    def get(self, sandbox: SandboxRef, session_id: str) -> PtySession:
        """Get details for a single PTY session."""
        data: PtySessionInfoDict = self._transport.request_json("GET", f"/v1/sandbox/{sandbox_id_of(sandbox)}/pty/{session_id}")  # type: ignore[assignment]
        return PtySession.from_dict(data)

    def delete(self, sandbox: SandboxRef, session_id: str) -> None:
        """Kill the shell process and remove the session."""
        self._transport.request("DELETE", f"/v1/sandbox/{sandbox_id_of(sandbox)}/pty/{session_id}", expected_status=204)

    def resize(self, sandbox: SandboxRef, session_id: str, *, cols: int, rows: int) -> PtySession:
        """Change the terminal dimensions while connected."""
        data: PtySessionInfoDict = self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/pty/{session_id}/resize", json={"cols": cols, "rows": rows})  # type: ignore[assignment]
        return PtySession.from_dict(data)

    def websocket_url(self, sandbox: SandboxRef, session_id: str) -> str:
        """Build the WSS URL for connecting to a PTY session."""
        return websocket_url_from_http(f"{self._transport.base_url}/v1/sandbox/{sandbox_id_of(sandbox)}/pty/{session_id}/connect")

    def connect(self, sandbox: SandboxRef, session_id: str, **kwargs: Any) -> PtyConnection:
        """Open a WebSocket connection for interactive terminal I/O.

        Returns a :class:`PtyConnection` with ``send``, ``recv``, and
        ``close`` methods. All messages are binary frames containing raw
        terminal bytes.
        """
        url = self.websocket_url(sandbox, session_id)
        try:
            websocket = connect(url, additional_headers={self._transport.auth_header: self._transport.auth_value}, **kwargs)
        except Exception as exc:
            raise Leap0WebSocketError(str(exc)) from exc
        return PtyConnection(websocket=websocket)
