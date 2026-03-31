from __future__ import annotations

import base64


def b64encode_bytes(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def b64encode_text(value: str, encoding: str = "utf-8") -> str:
    return b64encode_bytes(value.encode(encoding))


def b64decode_text(value: str, encoding: str = "utf-8") -> str:
    return base64.b64decode(value).decode(encoding)


def b64decode_bytes(value: str) -> bytes:
    return base64.b64decode(value)
