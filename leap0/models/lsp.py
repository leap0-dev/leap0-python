from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .._schemas.lsp import LspJsonRpcErrorDict, LspJsonRpcResponseDict, LspSuccessResponseDict

@dataclass(slots=True)
class LspResponse:
    """Basic response from LSP lifecycle operations."""
    success: bool = False

    @classmethod
    def from_dict(cls, data: LspSuccessResponseDict) -> LspResponse:
        """Build an instance from a wire-format dictionary."""
        return cls(success=bool(data.get("success", False)))

@dataclass(slots=True)
class LspJsonRpcError:
    """JSON-RPC error returned by an LSP operation."""
    code: int = 0
    message: str = ""
    data: Any = None

    @classmethod
    def from_dict(cls, data: LspJsonRpcErrorDict) -> LspJsonRpcError:
        """Build an instance from a wire-format dictionary."""
        return cls(
            code=int(data.get("code", 0)),
            message=data.get("message", ""),
            data=data.get("data"),
        )

@dataclass(slots=True)
class LspJsonRpcResponse:
    """JSON-RPC response returned by an LSP operation."""
    jsonrpc: str = ""
    id: int | str | None = None
    result: Any = None
    error: LspJsonRpcError | None = None

    @classmethod
    def from_dict(cls, data: LspJsonRpcResponseDict) -> LspJsonRpcResponse:
        """Build an instance from a wire-format dictionary."""
        error = data.get("error")
        return cls(
            jsonrpc=data.get("jsonrpc", ""),
            id=data.get("id"),
            result=data.get("result"),
            error=LspJsonRpcError.from_dict(error) if isinstance(error, dict) else None,
        )
