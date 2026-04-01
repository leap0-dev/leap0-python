from __future__ import annotations

from dataclasses import dataclass, field
from pydantic import BaseModel, ConfigDict, model_validator
from websockets.sync.client import ClientConnection
from .._schemas.pty import PtyListResponseDict, PtySessionInfoDict

class CreatePtySessionParams(BaseModel):
    """Validated PTY session creation parameters."""
    model_config = ConfigDict(extra="forbid")

    session_id: str | None = None
    cols: int | None = None
    rows: int | None = None
    cwd: str | None = None
    envs: dict[str, str] | None = None
    lazy_start: bool | None = None

    @model_validator(mode="after")
    def _validate_values(self) -> CreatePtySessionParams:
        if self.session_id is not None and not self.session_id.strip():
            raise ValueError("session_id must be a non-empty string when provided")
        if self.cols is not None and self.cols < 1:
            raise ValueError("cols must be at least 1 when provided")
        if self.rows is not None and self.rows < 1:
            raise ValueError("rows must be at least 1 when provided")
        if self.cwd is not None and not self.cwd.strip():
            raise ValueError("cwd must be a non-empty string when provided")
        if self.session_id is not None:
            self.session_id = self.session_id.strip()
        if self.cwd is not None:
            self.cwd = self.cwd.strip()
        return self

    def to_payload(self) -> dict[str, object]:
        """Convert this object to an API request payload."""
        payload = self.model_dump(exclude_none=True)
        session_id = payload.pop("session_id", None)
        if session_id is not None:
            payload["id"] = session_id
        return payload

@dataclass(slots=True)
class PtySession:
    """PTY session metadata."""
    id: str = ""
    cwd: str = ""
    envs: dict[str, str] = field(default_factory=dict)
    cols: int = 0
    rows: int = 0
    created_at: str = ""
    active: bool = False
    lazy_start: bool = False

    @classmethod
    def from_dict(cls, data: PtySessionInfoDict) -> PtySession:
        """Build an instance from a wire-format dictionary."""
        return cls(
            id=data.get("id", ""),
            cwd=data.get("cwd", ""),
            envs=data.get("envs") or {},
            cols=int(data.get("cols", 0)),
            rows=int(data.get("rows", 0)),
            created_at=data.get("created_at", ""),
            active=bool(data.get("active", False)),
            lazy_start=bool(data.get("lazy_start", False)),
        )

@dataclass(slots=True)
class PtyConnection:
    """Synchronous PTY websocket connection wrapper."""
    websocket: ClientConnection

    def send(self, data: str | bytes) -> None:
        """Send data through the PTY websocket connection."""
        payload = data.encode() if isinstance(data, str) else data
        self.websocket.send(payload)

    def recv(self) -> bytes:
        """Receive data from the PTY websocket connection."""
        message = self.websocket.recv()
        if isinstance(message, str):
            return message.encode()
        if isinstance(message, bytes):
            return message
        raise TypeError(f"Unexpected message type from websocket: {type(message).__name__}")

    def close(self) -> None:
        """Close the client and release resources."""
        self.websocket.close()
