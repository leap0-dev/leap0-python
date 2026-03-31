from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, TypedDict


RegistryCredentialType = Literal["basic", "aws", "gcp", "azure"]


class RegistryCredentialsDict(TypedDict, total=False):
    type: RegistryCredentialType
    username: str
    password: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    gcp_service_account_json: str
    azure_client_id: str
    azure_client_secret: str
    azure_tenant_id: str


class ImageConfigDict(TypedDict, total=False):
    entrypoint: list[str] | None
    cmd: list[str] | None
    working_dir: str | None
    user: str
    env: dict[str, Any] | None


class UploadTemplateResponseDict(TypedDict):
    id: str
    name: str
    digest: str
    image_config: ImageConfigDict | None
    is_system: bool
    created_at: str


@dataclass(slots=True)
class ImageConfig:
    entrypoint: list[str] = field(default_factory=list)
    cmd: list[str] = field(default_factory=list)
    working_dir: str | None = None
    user: str = ""
    env: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: ImageConfigDict) -> ImageConfig:
        return cls(
            entrypoint=data.get("entrypoint") or [],
            cmd=data.get("cmd") or [],
            working_dir=data.get("working_dir"),
            user=data.get("user", ""),
            env=data.get("env"),
        )


@dataclass(slots=True)
class Template:
    id: str
    name: str
    digest: str = ""
    image_config: ImageConfig | None = None
    is_system: bool = False
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: UploadTemplateResponseDict) -> Template:
        ic = data.get("image_config")
        return cls(
            id=data.get("id", ""),  # type: ignore[arg-type]
            name=data.get("name", ""),  # type: ignore[arg-type]
            digest=data.get("digest", ""),  # type: ignore[arg-type]
            image_config=ImageConfig.from_dict(ic) if isinstance(ic, dict) else None,
            is_system=bool(data.get("is_system", False)),  # type: ignore[arg-type]
            created_at=data.get("created_at", ""),  # type: ignore[arg-type]
        )
