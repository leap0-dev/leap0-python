from __future__ import annotations

from collections.abc import Mapping

from .._internal.types import JsonObject
from .env import expand_env


def build_command_payload(*, command: str, cwd: str | None = None, timeout: int | None = None, env: Mapping[str, str] | None = None) -> JsonObject:
    payload: JsonObject = {"command": expand_env(command, env) if env else command}
    if cwd is not None:
        payload["cwd"] = expand_env(cwd, env) if env else cwd
    if timeout is not None:
        payload["timeout"] = timeout
    return payload
