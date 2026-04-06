from __future__ import annotations

import json
from collections.abc import AsyncIterable, Iterable
from typing import Any, AsyncIterator, Iterator


def iter_ndjson(lines: Iterable[str]) -> Iterator[dict[str, Any]]:
    """Yield JSON objects from newline-delimited JSON input."""
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


def _parse_sse_data(data: str) -> dict[str, Any] | str:
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError:
        return data
    return parsed if isinstance(parsed, dict) else data


def _emit_sse_event(buffer: list[str]) -> dict[str, Any] | str | None:
    data_lines = [_sse_data_value(item) for item in buffer if item.startswith("data:")]
    if not data_lines:
        return None

    event_name: str | None = None
    for item in buffer:
        if item.startswith("event:"):
            event_name = item[6:].lstrip(" ")

    data = "\n".join(data_lines)
    if event_name == "error":
        return {"error": data}
    return _parse_sse_data(data)


def iter_sse_events(lines: Iterable[str]) -> Iterator[dict[str, Any] | str]:
    """Yield parsed events from an SSE line iterator."""
    buffer: list[str] = []
    for line in lines:
        stripped = line.rstrip("\r\n")
        if stripped == "":
            if buffer:
                event = _emit_sse_event(buffer)
                if event is not None:
                    yield event
                buffer.clear()
            continue
        if stripped.startswith(":"):
            continue
        buffer.append(stripped)
    if buffer:
        event = _emit_sse_event(buffer)
        if event is not None:
            yield event


async def aiter_sse_events(lines: AsyncIterable[str]) -> AsyncIterator[dict[str, Any] | str]:
    """Yield parsed events from an asynchronous SSE line iterator."""
    buffer: list[str] = []
    async for line in lines:
        stripped = line.rstrip("\r\n")
        if stripped == "":
            if buffer:
                event = _emit_sse_event(buffer)
                if event is not None:
                    yield event
                buffer.clear()
            continue
        if stripped.startswith(":"):
            continue
        buffer.append(stripped)
    if buffer:
        event = _emit_sse_event(buffer)
        if event is not None:
            yield event
