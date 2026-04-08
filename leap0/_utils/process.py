from __future__ import annotations

from collections.abc import Mapping

from .._internal.types import JsonObject


def build_command_payload(*, command: str, cwd: str | None = None, env: Mapping[str, str] | None = None, timeout: int | None = None) -> JsonObject:
    """Build the request payload for one-shot process execution."""
    payload: JsonObject = {"command": command}
    if cwd is not None:
        payload["cwd"] = cwd
    if env is not None:
        payload["envs"] = dict(env)
    if timeout is not None:
        payload["timeout"] = timeout
    return payload
