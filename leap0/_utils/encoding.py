from __future__ import annotations

import base64


def b64encode_bytes(value: bytes) -> str:
    """Encode bytes as a base64 string."""
    return base64.b64encode(value).decode("ascii")


def b64encode_text(value: str, encoding: str = "utf-8") -> str:
    """Encode text as base64 using UTF-8."""
    return b64encode_bytes(value.encode(encoding))


def b64decode_text(value: str, encoding: str = "utf-8") -> str:
    """Decode a base64 string into UTF-8 text."""
    return base64.b64decode(value).decode(encoding)


def b64decode_bytes(value: str) -> bytes:
    """Decode a base64 string into raw bytes."""
    return base64.b64decode(value)
