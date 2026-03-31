from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TypedDict

from typing_extensions import Literal, NotRequired, Required, TypeAlias


class RegistryCredentialType(str, Enum):
    BASIC = "basic"
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"


class BasicRegistryCredentialsDict(TypedDict, total=False):
    type: Required[Literal[RegistryCredentialType.BASIC, "basic"]]
    username: Required[str]
    password: Required[str]


class AwsRegistryCredentialsDict(TypedDict, total=False):
    type: Required[Literal[RegistryCredentialType.AWS, "aws"]]
    aws_access_key_id: Required[str]
    aws_secret_access_key: Required[str]
    aws_region: NotRequired[str]


class GcpRegistryCredentialsDict(TypedDict, total=False):
    type: Required[Literal[RegistryCredentialType.GCP, "gcp"]]
    gcp_service_account_json: Required[str]


class AzureRegistryCredentialsDict(TypedDict, total=False):
    type: Required[Literal[RegistryCredentialType.AZURE, "azure"]]
    azure_client_id: Required[str]
    azure_client_secret: Required[str]
    azure_tenant_id: Required[str]


RegistryCredentialsDict: TypeAlias = (
    BasicRegistryCredentialsDict
    | AwsRegistryCredentialsDict
    | GcpRegistryCredentialsDict
    | AzureRegistryCredentialsDict
)


class ImageConfigDict(TypedDict, total=False):
    entrypoint: list[str] | None
    cmd: list[str] | None
    working_dir: str
    user: str
    env: dict[str, str] | None


class UploadTemplateResponseDict(TypedDict):
    id: str
    name: str
    digest: str
    image_config: ImageConfigDict | None
    is_system: bool
    created_at: str


@dataclass(slots=True)
class ImageConfig:
    entrypoint: list[str] | None = None
    cmd: list[str] | None = None
    working_dir: str = ""
    user: str = ""
    env: dict[str, str] | None = None

    @classmethod
    def from_dict(cls, data: ImageConfigDict) -> ImageConfig:
        return cls(
            entrypoint=data.get("entrypoint"),
            cmd=data.get("cmd"),
            working_dir=data.get("working_dir", ""),
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
