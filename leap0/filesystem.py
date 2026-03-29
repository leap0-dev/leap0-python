from __future__ import annotations

from typing import Any

from ._transport import Transport
from ._types import (
    EditFileResponseDict,
    EditFilesResponseDict,
    ExistsResponseDict,
    FileInfoDict,
    GlobResponseDict,
    GrepResponseDict,
    LsResponseDict,
    TreeResponseDict,
)
from .models import (
    EditFileResult,
    EditResult,
    FileEdit,
    FileInfo,
    LsResult,
    SandboxRef,
    SearchMatch,
    TreeResult,
    sandbox_id_of,
)


class FilesystemClient:
    """List, read, write, move, copy, delete, and search files inside a sandbox.

    File content is transferred as raw binary bytes.
    """

    def __init__(self, transport: Transport):
        self._transport = transport

    def ls(self, sandbox: SandboxRef, *, path: str, recursive: bool = False, exclude: list[str] | None = None) -> LsResult:
        """List directory entries.

        Args:
            sandbox: Sandbox ID or object.
            path: Directory path to list.
            recursive: List recursively.
            exclude: Glob patterns to exclude.
        """
        payload: dict[str, Any] = {"path": path, "recursive": recursive}
        if exclude is not None:
            payload["exclude"] = exclude
        data: LsResponseDict = self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/ls", json=payload)  # type: ignore[assignment]
        return LsResult.from_dict(data)

    def stat(self, sandbox: SandboxRef, *, path: str) -> FileInfo:
        """Get metadata for a single path."""
        data: FileInfoDict = self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/stat", json={"path": path})  # type: ignore[assignment]
        return FileInfo.from_dict(data)

    def mkdir(self, sandbox: SandboxRef, *, path: str, recursive: bool = False, permissions: str | None = None) -> None:
        """Create a directory. Set *recursive* to create parent directories.

        Args:
            sandbox: Sandbox ID or object.
            path: Directory path to create.
            recursive: Create parents as needed.
            permissions: Octal permission string (e.g. ``"755"``).
        """
        payload: dict[str, Any] = {"path": path, "recursive": recursive}
        if permissions is not None:
            payload["permissions"] = permissions
        self._transport.request(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/mkdir",
            json=payload,
            expected_status=204,
        )

    def write_file_bytes(self, sandbox: SandboxRef, *, path: str, content: bytes, permissions: str | None = None) -> None:
        """Write raw bytes to a single file path."""
        params: dict[str, str] = {"path": path}
        if permissions is not None:
            params["permissions"] = permissions
        self._transport.request(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/write-file",
            params=params,
            content=content,
            headers={"Content-Type": "application/octet-stream"},
            expected_status=204,
        )

    def write_file_text(self, sandbox: SandboxRef, *, path: str, content: str, encoding: str = "utf-8", permissions: str | None = None) -> None:
        """Write a string to a single file path, encoded as *encoding*."""
        self.write_file_bytes(sandbox, path=path, content=content.encode(encoding), permissions=permissions)

    def write_files_bytes(self, sandbox: SandboxRef, *, files: dict[str, bytes]) -> None:
        """Write multiple files in a single request.

        Args:
            sandbox: Sandbox ID or object.
            files: Mapping of file path to raw bytes content.
        """
        self._transport.request(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/write-files",
            files=[(path, data) for path, data in files.items()],
            expected_status=204,
        )

    def write_files_text(self, sandbox: SandboxRef, *, files: dict[str, str], encoding: str = "utf-8") -> None:
        """Write multiple text files in a single request."""
        self.write_files_bytes(sandbox, files={p: c.encode(encoding) for p, c in files.items()})

    def read_file_bytes(
        self,
        sandbox: SandboxRef,
        *,
        path: str,
        offset: int | None = None,
        limit: int | None = None,
        head: int | None = None,
        tail: int | None = None,
    ) -> bytes:
        """Read a single file and return its raw bytes.

        Args:
            sandbox: Sandbox ID or object.
            path: Path to the file.
            offset: Byte offset to start from.
            limit: Maximum bytes to read.
            head: Return only the first N lines (mutually exclusive with *tail*).
            tail: Return only the last N lines (mutually exclusive with *head*).
        """
        payload: dict[str, Any] = {"path": path}
        if offset is not None:
            payload["offset"] = offset
        if limit is not None:
            payload["limit"] = limit
        if head is not None:
            payload["head"] = head
        if tail is not None:
            payload["tail"] = tail
        response = self._transport.request("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/read-file", json=payload)
        return response.content

    def read_file_text(
        self,
        sandbox: SandboxRef,
        *,
        path: str,
        offset: int | None = None,
        limit: int | None = None,
        head: int | None = None,
        tail: int | None = None,
        encoding: str = "utf-8",
    ) -> str:
        """Read a single file and return its content decoded as a string."""
        return self.read_file_bytes(
            sandbox,
            path=path,
            offset=offset,
            limit=limit,
            head=head,
            tail=tail,
        ).decode(encoding)

    def read_files_bytes(self, sandbox: SandboxRef, *, paths: list[str]) -> dict[str, bytes]:
        """Read multiple files. Returns a mapping of file path to raw bytes."""
        response = self._transport.request("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/read-files", json={"paths": paths})
        return _parse_multipart_response(response.headers.get("content-type", ""), response.content)

    def read_files_text(self, sandbox: SandboxRef, *, paths: list[str], encoding: str = "utf-8") -> dict[str, str]:
        """Read multiple files. Returns a mapping of file path to decoded string."""
        return {path: content.decode(encoding) for path, content in self.read_files_bytes(sandbox, paths=paths).items()}

    def delete(self, sandbox: SandboxRef, *, path: str, recursive: bool = False) -> None:
        """Delete a file or directory. Set *recursive* for directories with contents."""
        self._transport.request(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/delete",
            json={"path": path, "recursive": recursive},
            expected_status=204,
        )

    def set_permissions(
        self,
        sandbox: SandboxRef,
        *,
        path: str,
        mode: str | None = None,
        owner: str | None = None,
        group: str | None = None,
    ) -> None:
        """Set file mode and optionally change owner and group."""
        payload: dict[str, Any] = {"path": path}
        if mode is not None:
            payload["mode"] = mode
        if owner is not None:
            payload["owner"] = owner
        if group is not None:
            payload["group"] = group
        self._transport.request("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/set-permissions", json=payload, expected_status=204)

    def glob(self, sandbox: SandboxRef, *, path: str, pattern: str, exclude: list[str] | None = None) -> list[str]:
        """Find file paths matching a glob pattern."""
        payload: dict[str, Any] = {"path": path, "pattern": pattern}
        if exclude is not None:
            payload["exclude"] = exclude
        data: GlobResponseDict = self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/glob", json=payload)  # type: ignore[assignment]
        return list(data.get("items", []))

    def grep(self, sandbox: SandboxRef, *, path: str, pattern: str, include: str | None = None, exclude: list[str] | None = None) -> list[SearchMatch]:
        """Search for a text pattern across files in a directory.

        Args:
            sandbox: Sandbox ID or object.
            path: Base directory to search from.
            pattern: Text pattern to search for.
            include: File pattern filter (e.g. ``"*.py"``).
            exclude: Glob patterns to exclude.
        """
        payload: dict[str, Any] = {"path": path, "pattern": pattern}
        if include is not None:
            payload["include"] = include
        if exclude is not None:
            payload["exclude"] = exclude
        data: GrepResponseDict = self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/grep", json=payload)  # type: ignore[assignment]
        return [SearchMatch.from_dict(item) for item in data.get("items", [])]

    def edit_file(self, sandbox: SandboxRef, *, path: str, edits: list[FileEdit]) -> EditFileResult:
        """Apply one or more find-and-replace edits to a single file.

        Returns the unified diff and total number of replacements made.
        """
        data: EditFileResponseDict = self._transport.request_json(  # type: ignore[assignment]
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/edit-file",
            json={"path": path, "edits": [e.to_dict() for e in edits]},
        )
        return EditFileResult.from_dict(data)

    def edit_files(self, sandbox: SandboxRef, *, paths: list[str], find: str, replace: str = "") -> list[EditResult]:
        """Replace text across multiple files at once."""
        data: EditFilesResponseDict = self._transport.request_json(  # type: ignore[assignment]
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/edit-files",
            json={"files": paths, "find": find, "replace": replace},
        )
        return [EditResult.from_dict(item) for item in data.get("items", [])]

    def move(self, sandbox: SandboxRef, *, src_path: str, dst_path: str, overwrite: bool = False) -> None:
        """Move or rename a file or directory."""
        self._transport.request(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/move",
            json={"src_path": src_path, "dst_path": dst_path, "overwrite": overwrite},
            expected_status=204,
        )

    def copy(
        self,
        sandbox: SandboxRef,
        *,
        src_path: str,
        dst_path: str,
        recursive: bool = False,
        overwrite: bool | None = None,
    ) -> None:
        """Copy a file or directory. Set *recursive* to copy directories with contents."""
        payload: dict[str, Any] = {"src_path": src_path, "dst_path": dst_path, "recursive": recursive}
        if overwrite is not None:
            payload["overwrite"] = overwrite
        self._transport.request("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/copy", json=payload, expected_status=204)

    def exists(self, sandbox: SandboxRef, *, path: str) -> bool:
        """Check whether a path exists in the sandbox."""
        data: ExistsResponseDict = self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/exists", json={"path": path})  # type: ignore[assignment]
        return bool(data.get("exists", False))

    def tree(self, sandbox: SandboxRef, *, path: str, max_depth: int | None = None, exclude: list[str] | None = None) -> TreeResult:
        """Get a recursive directory tree.

        Args:
            sandbox: Sandbox ID or object.
            path: Root directory path.
            max_depth: Maximum traversal depth.
            exclude: Glob patterns to exclude.
        """
        payload: dict[str, Any] = {"path": path}
        if max_depth is not None:
            payload["max_depth"] = max_depth
        if exclude is not None:
            payload["exclude"] = exclude
        data: TreeResponseDict = self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/tree", json=payload)  # type: ignore[assignment]
        return TreeResult.from_dict(data)


def _parse_multipart_response(content_type: str, body: bytes) -> dict[str, bytes]:
    from email.parser import BytesParser

    raw = f"Content-Type: {content_type}\r\n\r\n".encode() + body
    msg = BytesParser().parsebytes(raw)

    result: dict[str, bytes] = {}
    if not msg.is_multipart():
        body_preview = body[:200] if len(body) > 200 else body
        raise ValueError(
            f"Expected multipart response but got content_type={content_type!r} "
            f"(body length={len(body)}, preview={body_preview!r})"
        )
    for part in msg.get_payload():  # type: ignore[union-attr]
        name = part.get_param("name", header="content-disposition")
        if name:
            payload = part.get_payload(decode=True)
            if payload is not None:
                result[str(name)] = payload
    return result
