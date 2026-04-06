from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator, model_validator

from .._schemas.filesystem import EditFileResponseDict, EditFilesResponseDict, EditResultDict, ExistsResponseDict, FileInfoDict, GlobResponseDict, GrepResponseDict, LsResponseDict, SearchMatchDict, TreeEntryDict, TreeResponseDict


class ReadFileParams(BaseModel):
    """Validated request parameters for reading a single file."""

    model_config = ConfigDict(extra="forbid")

    path: str
    offset: int | None = None
    limit: int | None = None
    head: int | None = None
    tail: int | None = None

    @model_validator(mode="after")
    def _validate_head_tail(self) -> "ReadFileParams":
        if self.head is not None and self.tail is not None:
            raise ValueError("`head` and `tail` are mutually exclusive")
        return self


NonEmptyOptionalString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class SetPermissionsParams(BaseModel):
    """Validated request parameters for the set-permissions endpoint."""

    model_config = ConfigDict(extra="forbid")

    path: str
    mode: NonEmptyOptionalString | None = None
    owner: NonEmptyOptionalString | None = None
    group: NonEmptyOptionalString | None = None

    @field_validator("mode", "owner", "group", mode="before")
    @classmethod
    def _validate_non_empty_string(cls, value: str | None, info: object) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        if not trimmed:
            field_name = getattr(info, "field_name", "value")
            raise ValueError(f"set_permissions {field_name} must be a non-empty string")
        return trimmed

    @model_validator(mode="after")
    def _validate_updates(self) -> "SetPermissionsParams":
        if self.mode is None and self.owner is None and self.group is None:
            raise ValueError("set_permissions requires at least one of mode, owner, or group")
        return self

@dataclass(slots=True)
class FileInfo:
    """Filesystem metadata for a path inside a sandbox.

    Attributes:
        name: Basename of the entry.
        path: Full sandbox path.
        is_dir: Whether the entry is a directory.
        size: File size in bytes.
        mode: POSIX mode string when available.
        mtime: Last modification time as a unix timestamp.
        owner: Entry owner.
        group: Entry group.
        is_symlink: Whether the entry is a symbolic link.
        link_target: Symlink target when present.
    """
    name: str
    path: str
    is_dir: bool = False
    size: int = 0
    mode: str = ""
    mtime: int = 0
    owner: str = ""
    group: str = ""
    is_symlink: bool = False
    link_target: str = ""

    @classmethod
    def from_dict(cls, data: FileInfoDict) -> FileInfo:
        """Build a file info object from a wire-format dictionary.

        Args:
            data: File metadata payload returned by the API.

        Returns:
            FileInfo: Parsed file info object.
        """
        return cls(
            name=data.get("name", ""),
            path=data.get("path", ""),
            is_dir=bool(data.get("is_dir", False)),
            size=int(data.get("size", 0)),
            mode=data.get("mode", ""),
            mtime=int(data.get("mtime", 0)),
            owner=data.get("owner", ""),
            group=data.get("group", ""),
            is_symlink=bool(data.get("is_symlink", False)),
            link_target=data.get("link_target", ""),
        )

@dataclass(slots=True)
class LsResult:
    """Directory listing result.

    Attributes:
        items: Entries returned for the requested directory.
    """
    items: list[FileInfo]

    @classmethod
    def from_dict(cls, data: LsResponseDict) -> LsResult:
        """Build a directory listing result from a wire-format dictionary.

        Args:
            data: Directory listing payload returned by the API.

        Returns:
            LsResult: Parsed listing result.
        """
        return cls(items=[FileInfo.from_dict(item) for item in data.get("items", [])])

@dataclass(slots=True)
class FileEdit:
    """Single find-and-replace edit specification.

    Attributes:
        find: Text to search for.
        replace: Replacement text.
    """
    find: str
    replace: str = ""

    def to_dict(self) -> dict[str, str]:
        """Convert this edit specification to an API payload.

        Returns:
            dict[str, str]: Serialized edit specification.
        """
        return {"find": self.find, "replace": self.replace}

@dataclass(slots=True)
class EditFileResult:
    """Result of editing a single file.

    Attributes:
        diff: Unified diff describing the edit.
        replacements: Number of replacements applied.
    """
    diff: str = ""
    replacements: int = 0

    @classmethod
    def from_dict(cls, data: EditFileResponseDict) -> EditFileResult:
        """Build a single-file edit result from a wire-format dictionary.

        Args:
            data: Edit result payload returned by the API.

        Returns:
            EditFileResult: Parsed edit result.
        """
        return cls(
            diff=data.get("diff", ""),
            replacements=int(data.get("replacements", 0)),
        )

@dataclass(slots=True)
class EditResult:
    """Result of editing one file in a multi-file edit operation."""
    file: str = ""
    success: bool = False
    error: str = ""

    @classmethod
    def from_dict(cls, data: EditResultDict) -> EditResult:
        """Build an instance from a wire-format dictionary."""
        return cls(
            file=data.get("file", ""),
            success=bool(data.get("success", False)),
            error=data.get("error", ""),
        )

@dataclass(slots=True)
class SearchMatch:
    """Single filesystem search or grep match."""
    path: str = ""
    line: int = 0
    content: str = ""

    @classmethod
    def from_dict(cls, data: SearchMatchDict) -> SearchMatch:
        """Build an instance from a wire-format dictionary."""
        return cls(
            path=data.get("path", ""),
            line=int(data.get("line", 0)),
            content=data.get("content", ""),
        )

@dataclass(slots=True)
class TreeEntry:
    """Single entry in a filesystem tree response."""
    name: str
    type: str = "file"
    children: list[TreeEntry] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: TreeEntryDict) -> TreeEntry:
        """Build an instance from a wire-format dictionary."""
        return cls(
            name=data.get("name", ""),
            type=data.get("type", "file"),
            children=[TreeEntry.from_dict(c) for c in data.get("children", [])],
        )

@dataclass(slots=True)
class TreeResult:
    """Recursive filesystem tree result."""
    items: list[TreeEntry]

    @classmethod
    def from_dict(cls, data: TreeResponseDict) -> TreeResult:
        """Build an instance from a wire-format dictionary."""
        return cls(items=[TreeEntry.from_dict(item) for item in data.get("items", [])])
