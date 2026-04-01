from __future__ import annotations

from typing import TypedDict

class FileInfoDict(TypedDict, total=False):
    """Wire schema for file metadata."""
    name: str
    path: str
    is_dir: bool
    size: int
    mode: str
    mtime: int
    owner: str
    group: str
    is_symlink: bool
    link_target: str

class LsResponseDict(TypedDict):
    """Wire schema for directory listings."""
    items: list[FileInfoDict]

class GlobResponseDict(TypedDict):
    """Wire schema for glob results."""
    items: list[str]

class SearchMatchDict(TypedDict, total=False):
    """Wire schema for a filesystem search match."""
    path: str
    line: int
    content: str

class GrepResponseDict(TypedDict):
    """Wire schema for grep results."""
    items: list[SearchMatchDict]

class EditFileResponseDict(TypedDict, total=False):
    """Wire schema for a single-file edit response."""
    diff: str
    replacements: int

class EditResultDict(TypedDict, total=False):
    """Wire schema for a per-file edit result."""
    file: str
    success: bool
    error: str

class EditFilesResponseDict(TypedDict):
    """Wire schema for a multi-file edit response."""
    items: list[EditResultDict]

class ExistsResponseDict(TypedDict):
    """Wire schema for path existence checks."""
    exists: bool

class TreeEntryDict(TypedDict, total=False):
    """Wire schema for one tree entry."""
    name: str
    type: str
    children: list[TreeEntryDict]

class TreeResponseDict(TypedDict):
    """Wire schema for recursive tree results."""
    items: list[TreeEntryDict]
