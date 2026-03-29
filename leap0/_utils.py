from __future__ import annotations

import base64
import json
from typing import Any, Iterable, Iterator


def b64encode_bytes(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def b64encode_text(value: str, encoding: str = "utf-8") -> str:
    return b64encode_bytes(value.encode(encoding))


def b64decode_text(value: str, encoding: str = "utf-8") -> str:
    return base64.b64decode(value).decode(encoding)


def b64decode_bytes(value: str) -> bytes:
    return base64.b64decode(value)


def ensure_leading_slash(value: str) -> str:
    return value if value.startswith("/") else f"/{value}"


def sandbox_base_url(sandbox_id: str, sandbox_domain: str | None, *, port: int | None = None) -> str:
    if not sandbox_domain:
        raise ValueError("sandbox_domain is required for sandbox host operations")
    host = f"{sandbox_id}.{sandbox_domain.strip('/')}"
    if port is not None:
        host = f"{port}-{host}"
    return f"https://{host}"


def websocket_url_from_http(url: str) -> str:
    if url.startswith("https://"):
        return url.replace("https://", "wss://", 1)
    if url.startswith("http://"):
        return url.replace("http://", "ws://", 1)
    return url


def file_uri(path: str) -> str:
    """Build a file:// URI for a sandbox-side absolute path."""
    clean = path if path.startswith("/") else f"/{path}"
    return f"file://{clean}"


def iter_ndjson(lines: Iterable[str]) -> Iterator[dict[str, Any]]:
    for line in lines:
        raw = line.strip()
        if raw:
            yield json.loads(raw)


def _sse_data_value(raw: str) -> str:
    """Extract the value from a 'data:' SSE field, stripping at most one leading space per spec."""
    value = raw[5:]
    if value.startswith(" "):
        value = value[1:]
    return value


def iter_sse_events(lines: Iterable[str]) -> Iterator[dict[str, Any]]:
    buffer: list[str] = []
    for line in lines:
        stripped = line.rstrip("\r")
        if stripped == "":
            if buffer:
                data_lines = [_sse_data_value(item) for item in buffer if item.startswith("data:")]
                if data_lines:
                    yield json.loads("\n".join(data_lines))
                buffer.clear()
            continue
        if stripped.startswith(":"):
            continue
        buffer.append(stripped)
    if buffer:
        data_lines = [_sse_data_value(item) for item in buffer if item.startswith("data:")]
        if data_lines:
            yield json.loads("\n".join(data_lines))
