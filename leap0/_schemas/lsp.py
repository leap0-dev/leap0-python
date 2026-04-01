from __future__ import annotations

from typing import Any, TypedDict

class LspSuccessResponseDict(TypedDict, total=False):
    """Wire schema for basic LSP success responses."""
    success: bool

class LspJsonRpcErrorDict(TypedDict, total=False):
    """Wire schema for LSP JSON-RPC errors."""
    code: int
    message: str
    data: Any

class LspJsonRpcResponseDict(TypedDict, total=False):
    """Wire schema for LSP JSON-RPC responses."""
    jsonrpc: str
    id: int | str | None
    result: Any
    error: LspJsonRpcErrorDict
