from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypedDict


class LspSuccessResponseDict(TypedDict, total=False):
    success: bool


class LspJsonRpcErrorDict(TypedDict, total=False):
    code: int
    message: str
    data: Any


class LspJsonRpcResponseDict(TypedDict, total=False):
    jsonrpc: str
    id: int | str | None
    result: Any
    error: LspJsonRpcErrorDict


@dataclass(slots=True)
class LspResponse:
    success: bool = False

    @classmethod
    def from_dict(cls, data: LspSuccessResponseDict) -> LspResponse:
        return cls(success=bool(data.get("success", False)))


@dataclass(slots=True)
class LspJsonRpcError:
    code: int = 0
    message: str = ""
    data: Any = None

    @classmethod
    def from_dict(cls, data: LspJsonRpcErrorDict) -> LspJsonRpcError:
        return cls(
            code=int(data.get("code", 0)),
            message=data.get("message", ""),
            data=data.get("data"),
        )


@dataclass(slots=True)
class LspJsonRpcResponse:
    jsonrpc: str = ""
    id: int | str | None = None
    result: Any = None
    error: LspJsonRpcError | None = None

    @classmethod
    def from_dict(cls, data: LspJsonRpcResponseDict) -> LspJsonRpcResponse:
        error = data.get("error")
        return cls(
            jsonrpc=data.get("jsonrpc", ""),
            id=data.get("id"),
            result=data.get("result"),
            error=LspJsonRpcError.from_dict(error) if isinstance(error, dict) else None,
        )
