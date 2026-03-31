from __future__ import annotations


def ensure_leading_slash(value: str) -> str:
    return value if value.startswith("/") else f"/{value}"


def sandbox_base_url(sandbox_id: str, sandbox_domain: str | None, *, port: int | None = None) -> str:
    if not sandbox_domain:
        raise ValueError("sandbox_domain is required for sandbox host operations")
    subdomain = f"{sandbox_id}-{port}" if port is not None else sandbox_id
    host = f"{subdomain}.{sandbox_domain.strip('/')}"
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
