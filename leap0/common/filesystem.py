from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypedDict


class FileInfoDict(TypedDict, total=False):
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
    items: list[FileInfoDict]


class GlobResponseDict(TypedDict):
    items: list[str]


class SearchMatchDict(TypedDict, total=False):
    path: str
    line: int
    content: str


class GrepResponseDict(TypedDict):
    items: list[SearchMatchDict]


class EditFileResponseDict(TypedDict, total=False):
    diff: str
    replacements: int


class EditResultDict(TypedDict, total=False):
    file: str
    success: bool
    error: str


class EditFilesResponseDict(TypedDict):
    items: list[EditResultDict]


class ExistsResponseDict(TypedDict):
    exists: bool


class TreeEntryDict(TypedDict, total=False):
    name: str
    type: str
    children: list[TreeEntryDict]


class TreeResponseDict(TypedDict):
    items: list[TreeEntryDict]


@dataclass(slots=True)
class FileInfo:
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
    items: list[FileInfo]

    @classmethod
    def from_dict(cls, data: LsResponseDict) -> LsResult:
        return cls(items=[FileInfo.from_dict(item) for item in data.get("items", [])])


@dataclass(slots=True)
class FileEdit:
    find: str
    replace: str = ""

    def to_dict(self) -> dict[str, str]:
        return {"find": self.find, "replace": self.replace}


@dataclass(slots=True)
class EditFileResult:
    diff: str = ""
    replacements: int = 0

    @classmethod
    def from_dict(cls, data: EditFileResponseDict) -> EditFileResult:
        return cls(
            diff=data.get("diff", ""),
            replacements=int(data.get("replacements", 0)),
        )


@dataclass(slots=True)
class EditResult:
    file: str = ""
    success: bool = False
    error: str = ""

    @classmethod
    def from_dict(cls, data: EditResultDict) -> EditResult:
        return cls(
            file=data.get("file", ""),
            success=bool(data.get("success", False)),
            error=data.get("error", ""),
        )


@dataclass(slots=True)
class SearchMatch:
    path: str = ""
    line: int = 0
    content: str = ""

    @classmethod
    def from_dict(cls, data: SearchMatchDict) -> SearchMatch:
        return cls(
            path=data.get("path", ""),
            line=int(data.get("line", 0)),
            content=data.get("content", ""),
        )


@dataclass(slots=True)
class TreeEntry:
    name: str
    type: str = "file"
    children: list[TreeEntry] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: TreeEntryDict) -> TreeEntry:
        return cls(
            name=data.get("name", ""),
            type=data.get("type", "file"),
            children=[TreeEntry.from_dict(c) for c in data.get("children", [])],
        )


@dataclass(slots=True)
class TreeResult:
    items: list[TreeEntry]

    @classmethod
    def from_dict(cls, data: TreeResponseDict) -> TreeResult:
        return cls(items=[TreeEntry.from_dict(item) for item in data.get("items", [])])
