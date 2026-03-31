from __future__ import annotations

import json
from typing import Any, Iterable, Iterator


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
