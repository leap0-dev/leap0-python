from __future__ import annotations

from email.parser import BytesParser


def parse_multipart_response(
    content_type: str,
    body: bytes,
    *,
    subject: str = "multipart body",
    operation: str | None = None,
) -> dict[str, bytes]:
    raw = f"Content-Type: {content_type}\r\n\r\n".encode() + body
    msg = BytesParser().parsebytes(raw)
    target = f"{operation} {subject}" if operation else subject

    result: dict[str, bytes] = {}
    if not msg.is_multipart():
        raise ValueError(
            f"Expected multipart response but got content_type={content_type!r} "
            f"(body length={len(body)}, preview='<redacted>')"
        )
    for part in msg.get_payload():  # type: ignore[union-attr]
        name = part.get_param("name", header="content-disposition")
        if not name:
            continue
        part_content_type = part.get_content_type()
        if part_content_type != "application/octet-stream":
            raise ValueError(
                f"Failed to parse {target}: expected file bytes for entry {name!r}, got {part_content_type}"
            )
        payload = part.get_payload(decode=True)
        if payload is None:
            raise ValueError(
                f"Failed to parse {target}: expected file bytes for entry {name!r}, got {part_content_type}"
            )
        result[str(name)] = payload
    return result
