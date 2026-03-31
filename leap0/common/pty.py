from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict

from websockets.sync.client import ClientConnection


class PtySessionInfoDict(TypedDict, total=False):
    id: str
    cwd: str
    envs: dict[str, str]
    cols: int
    rows: int
    created_at: str
    active: bool
    lazy_start: bool


class PtyListResponseDict(TypedDict, total=False):
    items: list[PtySessionInfoDict]


@dataclass(slots=True)
class PtySession:
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
    websocket: ClientConnection

    def send(self, data: str | bytes) -> None:
        payload = data.encode() if isinstance(data, str) else data
        self.websocket.send(payload)

    def recv(self) -> bytes:
        message = self.websocket.recv()
        if isinstance(message, str):
            return message.encode()
        if isinstance(message, bytes):
            return message
        raise TypeError(f"Unexpected message type from websocket: {type(message).__name__}")

    def close(self) -> None:
        self.websocket.close()
