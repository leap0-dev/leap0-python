from __future__ import annotations

from typing import Any, cast

from .._internal.types import JsonObject
from ..models.filesystem import EditFileResult, EditResult, FileEdit, FileInfo, LsResult, ReadFileParams, SearchMatch, SetPermissionsParams, TreeResult
from ..models.sandbox import SandboxRef, sandbox_id_of
from .._schemas.filesystem import EditFileResponseDict, EditFilesResponseDict, ExistsResponseDict, FileInfoDict, GlobResponseDict, GrepResponseDict, LsResponseDict, TreeResponseDict
from .._utils.errors import intercept_errors
from .._utils.multipart import parse_multipart_response
from ._transport import Transport


class FilesystemClient:
    """List, read, write, move, copy, delete, and search files inside a sandbox.
    
        Text helpers such as :meth:`write_file` and :meth:`read_file` provide the
        most ergonomic default API. Use the ``*_bytes`` variants when you need raw
        binary access or want to avoid text decoding.
        
    Attributes:
        None.
    """

    def __init__(self, transport: Transport):
        self._transport = transport

    @intercept_errors("Failed to list directory: ")
    def ls(self, sandbox: SandboxRef, *, path: str, recursive: bool = False, exclude: list[str] | None = None) -> LsResult:
        """List directory entries.
        
                Args:
                    sandbox: Sandbox ID or object.
                    path: Directory path to list.
                    recursive: List recursively.
                    exclude: Glob patterns to exclude.
        
        Returns:
            object: Result returned by this operation.
        """
        payload: JsonObject = {"path": path, "recursive": recursive}
        if exclude is not None:
            payload["exclude"] = exclude
        data = cast(LsResponseDict, self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/ls", json=payload))
        return LsResult.from_dict(data)

    @intercept_errors("Failed to stat file: ")
    def stat(self, sandbox: SandboxRef, *, path: str) -> FileInfo:
        """Get metadata for a single path.
        
        Args:
            sandbox: Sandbox ID or object.
            path: Path used by this operation.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(FileInfoDict, self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/stat", json={"path": path}))
        return FileInfo.from_dict(data)

    @intercept_errors("Failed to create directory: ")
    def mkdir(self, sandbox: SandboxRef, *, path: str, recursive: bool = False, permissions: str | None = None, http_timeout: float | None = None) -> None:
        """Create a directory. Set *recursive* to create parent directories.

        Args:
            sandbox: Sandbox ID or object.
            path: Directory path to create.
            recursive: Create parents as needed.
            permissions: Octal permission string (e.g. ``"755"``).
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        """
        payload: JsonObject = {"path": path, "recursive": recursive}
        if permissions is not None:
            payload["permissions"] = permissions
        self._transport.request(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/mkdir",
            json=payload,
            expected_status=204,
            timeout=http_timeout,
        )

    @intercept_errors("Failed to write file: ")
    def write_bytes(self, sandbox: SandboxRef, *, path: str, content: bytes, permissions: str | None = None, http_timeout: float | None = None) -> None:
        """Write raw bytes to a single file path.

        Args:
            sandbox: Sandbox ID or object.
            path: Destination file path.
            content: Raw file bytes.
            permissions: Optional octal permission string.

            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        Example:
            ```python
            sandbox.filesystem.write_bytes(
                path="/workspace/logo.png",
                content=image_bytes,
            )
            ```
        """
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
            timeout=http_timeout,
        )

    @intercept_errors("Failed to write file: ")
    def write_file(self, sandbox: SandboxRef, *, path: str, content: str, encoding: str = "utf-8", permissions: str | None = None, http_timeout: float | None = None) -> None:
        """Write text to a single file path.

        Args:
            sandbox: Sandbox ID or object.
            path: Destination file path.
            content: Text content to write.
            encoding: Text encoding used before upload.
            permissions: Optional octal permission string.

            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        Example:
            ```python
            sandbox.filesystem.write_file(
                path="/workspace/app.py",
                content="print('hello')\n",
            )
            ```
        """
        self.write_bytes(
            sandbox,
            path=path,
            content=content.encode(encoding),
            permissions=permissions,
            http_timeout=http_timeout,
        )

    @intercept_errors("Failed to write files: ")
    def write_files_bytes(self, sandbox: SandboxRef, *, files: dict[str, bytes], http_timeout: float | None = None) -> None:
        """Write multiple files in a single request.

        Args:
            sandbox: Sandbox ID or object.
            files: Mapping of file path to raw bytes content.

            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        Example:
            ```python
            sandbox.filesystem.write_files_bytes(
                files={"/workspace/a.bin": b"a", "/workspace/b.bin": b"b"},
            )
            ```
        """
        self._transport.request(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/write-files",
            files=[(path, data) for path, data in files.items()],
            expected_status=204,
            timeout=http_timeout,
        )

    @intercept_errors("Failed to write files: ")
    def write_files(self, sandbox: SandboxRef, *, files: dict[str, str], encoding: str = "utf-8", http_timeout: float | None = None) -> None:
        """Write multiple text files in a single request.

        Args:
            sandbox: Sandbox ID or object.
            files: Mapping of file path to text content.
            encoding: Text encoding used before upload.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        """
        self.write_files_bytes(
            sandbox,
            files={p: c.encode(encoding) for p, c in files.items()},
            http_timeout=http_timeout,
        )

    @intercept_errors("Failed to read file: ")
    def read_bytes(
        self,
        sandbox: SandboxRef,
        *,
        path: str,
        offset: int | None = None,
        limit: int | None = None,
        head: int | None = None,
        tail: int | None = None,
        http_timeout: float | None = None,
    ) -> bytes:
        """Read a single file and return its raw bytes.

        Args:
            sandbox: Sandbox ID or object.
            path: Path to the file.
            offset: Byte offset to start from.
            limit: Maximum bytes to read.
            head: Return only the first N lines (mutually exclusive with *tail*).
            tail: Return only the last N lines (mutually exclusive with *head*).
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            bytes: File contents as raw bytes.

        Example:
            ```python
            content = sandbox.filesystem.read_bytes(path="/workspace/logo.png")
            print(content)
            ```
        """
        payload = ReadFileParams(path=path, offset=offset, limit=limit, head=head, tail=tail).model_dump(exclude_none=True)
        response = self._transport.request("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/read-file", json=payload, timeout=http_timeout)
        return response.content

    @intercept_errors("Failed to read file: ")
    def read_file(
        self,
        sandbox: SandboxRef,
        *,
        path: str,
        offset: int | None = None,
        limit: int | None = None,
        head: int | None = None,
        tail: int | None = None,
        encoding: str = "utf-8",
        http_timeout: float | None = None,
    ) -> str:
        """Read a single file and return its content decoded as text.
        
        Args:
            sandbox: Sandbox ID or object.
            path: Path used by this operation.
            offset: Parameter for this operation.
            limit: Parameter for this operation.
            head: Parameter for this operation.
            tail: Parameter for this operation.
            encoding: Parameter for this operation.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        return self.read_bytes(
            sandbox,
            path=path,
            offset=offset,
            limit=limit,
            head=head,
            tail=tail,
            http_timeout=http_timeout,
        ).decode(encoding)

    @intercept_errors("Failed to read files: ")
    def read_files_bytes(
        self,
        sandbox: SandboxRef,
        *,
        paths: list[str],
        http_timeout: float | None = None,
    ) -> dict[str, bytes]:
        """Read multiple files and return raw bytes keyed by path.
        
        Args:
            sandbox: Sandbox ID or object.
            paths: Parameter for this operation.
        
        Returns:
            object: Result returned by this operation.
        """
        response = self._transport.request(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/read-files",
            json={"paths": paths},
            timeout=http_timeout,
        )
        return _parse_multipart_response(response.headers.get("content-type", ""), response.content)

    @intercept_errors("Failed to read files: ")
    def read_files(self, sandbox: SandboxRef, *, paths: list[str], encoding: str = "utf-8", http_timeout: float | None = None) -> dict[str, str]:
        """
                    Read multiple files and return decoded text keyed by path.
        
                    Args:
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        return {
            path: content.decode(encoding)
            for path, content in self.read_files_bytes(
                sandbox,
                paths=paths,
                http_timeout=http_timeout,
            ).items()
        }

    @intercept_errors("Failed to delete: ")
    def delete(self, sandbox: SandboxRef, *, path: str, recursive: bool = False, http_timeout: float | None = None) -> None:
        """Delete a file or directory.

        Args:
            sandbox: Sandbox ID or object.
            path: Path to delete.
            recursive: Required when deleting a non-empty directory.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        """
        self._transport.request(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/delete",
            json={"path": path, "recursive": recursive},
            expected_status=204,
            timeout=http_timeout,
        )

    @intercept_errors("Failed to set permissions: ")
    def set_permissions(
        self,
        sandbox: SandboxRef,
        *,
        path: str,
        mode: str | None = None,
        owner: str | None = None,
        group: str | None = None,
        http_timeout: float | None = None,
    ) -> None:
        """
            Set file mode and optionally change owner and group.

            Args:
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        """
        payload = SetPermissionsParams(path=path, mode=mode, owner=owner, group=group).model_dump(exclude_none=True)
        self._transport.request("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/set-permissions", json=payload, expected_status=204, timeout=http_timeout)

    @intercept_errors("Failed to glob: ")
    def glob(self, sandbox: SandboxRef, *, path: str, pattern: str, exclude: list[str] | None = None, http_timeout: float | None = None) -> list[str]:
        """Find file paths matching a glob pattern.

        Args:
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            list[str]: Matching file paths.
        """
        payload: JsonObject = {"path": path, "pattern": pattern}
        if exclude is not None:
            payload["exclude"] = exclude
        data = cast(GlobResponseDict, self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/glob", json=payload, timeout=http_timeout))
        return list(data.get("items", []))

    @intercept_errors("Failed to grep: ")
    def grep(self, sandbox: SandboxRef, *, path: str, pattern: str, include: str | None = None, exclude: list[str] | None = None, http_timeout: float | None = None) -> list[SearchMatch]:
        """Search for a text pattern across files in a directory.

        Args:
            sandbox: Sandbox ID or object.
            path: Base directory to search from.
            pattern: Text pattern to search for.
            include: File pattern filter (e.g. ``"*.py"``).
            exclude: Glob patterns to exclude.

            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Args:
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            list[SearchMatch]: Matching lines with file and line metadata.
        """
        payload: JsonObject = {"path": path, "pattern": pattern}
        if include is not None:
            payload["include"] = include
        if exclude is not None:
            payload["exclude"] = exclude
        data = cast(GrepResponseDict, self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/grep", json=payload, timeout=http_timeout))
        return [SearchMatch.from_dict(item) for item in data.get("items", [])]

    @intercept_errors("Failed to edit file: ")
    def edit_file(self, sandbox: SandboxRef, *, path: str, edits: list[FileEdit], http_timeout: float | None = None) -> EditFileResult:
        """Apply one or more find-and-replace edits to a single file.
        
                Returns:
                    EditFileResult: Unified diff and replacement count.
        
        Args:
            sandbox: Sandbox ID or object.
            path: Path used by this operation.
            edits: Parameter for this operation.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        """
        data = cast(EditFileResponseDict, self._transport.request_json(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/edit-file",
            json={"path": path, "edits": [e.to_dict() for e in edits]},
            timeout=http_timeout,
        ))
        return EditFileResult.from_dict(data)

    @intercept_errors("Failed to edit files: ")
    def edit_files(self, sandbox: SandboxRef, *, paths: list[str], find: str, replace: str = "", http_timeout: float | None = None) -> list[EditResult]:
        """Replace text across multiple files at once.

        Args:
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            list[EditResult]: Per-file edit results.
        """
        data = cast(EditFilesResponseDict, self._transport.request_json(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/edit-files",
            json={"files": paths, "find": find, "replace": replace},
            timeout=http_timeout,
        ))
        return [EditResult.from_dict(item) for item in data.get("items", [])]

    @intercept_errors("Failed to move: ")
    def move(self, sandbox: SandboxRef, *, src_path: str, dst_path: str, overwrite: bool = False, http_timeout: float | None = None) -> None:
        """Move or rename a file or directory.
        
        Args:
            sandbox: Sandbox ID or object.
            src_path: Parameter for this operation.
            dst_path: Parameter for this operation.
            overwrite: Parameter for this operation.
        """
        self._transport.request(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/move",
            json={"src_path": src_path, "dst_path": dst_path, "overwrite": overwrite},
            expected_status=204,
            timeout=http_timeout,
        )

    @intercept_errors("Failed to copy: ")
    def copy(
        self,
        sandbox: SandboxRef,
        *,
        src_path: str,
        dst_path: str,
        recursive: bool = False,
        overwrite: bool | None = None,
        http_timeout: float | None = None,
    ) -> None:
        """Copy a file or directory.

        Args:
            sandbox: Sandbox ID or object.
            src_path: Source path.
            dst_path: Destination path.
            recursive: Required when copying a directory.
            overwrite: Overwrite the destination if it already exists.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        """
        payload: JsonObject = {"src_path": src_path, "dst_path": dst_path, "recursive": recursive}
        if overwrite is not None:
            payload["overwrite"] = overwrite
        self._transport.request("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/copy", json=payload, expected_status=204, timeout=http_timeout)

    @intercept_errors("Failed to check path: ")
    def exists(self, sandbox: SandboxRef, *, path: str, http_timeout: float | None = None) -> bool:
        """Check whether a path exists in the sandbox.

        Args:
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            bool: ``True`` when the path exists.
        """
        data = cast(ExistsResponseDict, self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/exists", json={"path": path}, timeout=http_timeout))
        return bool(data.get("exists", False))

    @intercept_errors("Failed to get directory tree: ")
    def tree(self, sandbox: SandboxRef, *, path: str, max_depth: int | None = None, exclude: list[str] | None = None, http_timeout: float | None = None) -> TreeResult:
        """Get a recursive directory tree.

        Args:
            sandbox: Sandbox ID or object.
            path: Root directory path.
            max_depth: Maximum traversal depth.
            exclude: Glob patterns to exclude.

            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        Returns:
            TreeResult: Recursive directory tree rooted at ``path``.
        """
        payload: JsonObject = {"path": path}
        if max_depth is not None:
            payload["max_depth"] = max_depth
        if exclude is not None:
            payload["exclude"] = exclude
        data = cast(TreeResponseDict, self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/filesystem/tree", json=payload, timeout=http_timeout))
        return TreeResult.from_dict(data)


def _parse_multipart_response(content_type: str, body: bytes) -> dict[str, bytes]:
    return parse_multipart_response(content_type, body)
