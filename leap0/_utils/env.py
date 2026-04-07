from __future__ import annotations

import re
from collections.abc import Mapping


_ENV_REF_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


def expand_env(value: str, env: Mapping[str, str]) -> str:
    """Expand ``$NAME`` and ``${NAME}`` placeholders using the provided mapping."""
    return _ENV_REF_RE.sub(lambda match: env.get(match.group(1) or match.group(2), match.group(0)), value)
