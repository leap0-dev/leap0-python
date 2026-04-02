from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from .._schemas.template import (
    AwsRegistryCredentialsDict as _AwsRegistryCredentialsDict,
    AzureRegistryCredentialsDict as _AzureRegistryCredentialsDict,
    BasicRegistryCredentialsDict as _BasicRegistryCredentialsDict,
    GcpRegistryCredentialsDict as _GcpRegistryCredentialsDict,
    ImageConfigDict,
    UploadTemplateResponseDict,
)

BasicRegistryCredentialsDict: TypeAlias = _BasicRegistryCredentialsDict
AwsRegistryCredentialsDict: TypeAlias = _AwsRegistryCredentialsDict
GcpRegistryCredentialsDict: TypeAlias = _GcpRegistryCredentialsDict
AzureRegistryCredentialsDict: TypeAlias = _AzureRegistryCredentialsDict
RegistryCredentialsDict: TypeAlias = (
    BasicRegistryCredentialsDict
    | AwsRegistryCredentialsDict
    | GcpRegistryCredentialsDict
    | AzureRegistryCredentialsDict
)


class _RegistryCredentialsBase(BaseModel):
    """Validated registry credentials."""

    model_config = ConfigDict(extra="forbid")


class RegistryCredentialType(str, Enum):
    """Supported container registry credential types."""
    BASIC = "basic"
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"


class BasicRegistryCredentials(_RegistryCredentialsBase):
    """Validated basic-auth registry credentials."""

    type: Literal["basic"] = RegistryCredentialType.BASIC.value
    username: str
    password: str


class AwsRegistryCredentials(_RegistryCredentialsBase):
    """Validated AWS registry credentials."""

    type: Literal["aws"] = RegistryCredentialType.AWS.value
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str | None = None


class GcpRegistryCredentials(_RegistryCredentialsBase):
    """Validated GCP registry credentials."""

    type: Literal["gcp"] = RegistryCredentialType.GCP.value
    gcp_service_account_json: str


class AzureRegistryCredentials(_RegistryCredentialsBase):
    """Validated Azure registry credentials."""

    type: Literal["azure"] = RegistryCredentialType.AZURE.value
    azure_client_id: str
    azure_client_secret: str
    azure_tenant_id: str


RegistryCredentials: TypeAlias = Annotated[
    BasicRegistryCredentials | AwsRegistryCredentials | GcpRegistryCredentials | AzureRegistryCredentials,
    Field(discriminator="type"),
]
RegistryCredentialsInput: TypeAlias = RegistryCredentials | RegistryCredentialsDict

class CreateTemplateParams(BaseModel):
    """Validated template creation parameters."""
    model_config = ConfigDict(extra="forbid")

    name: str
    uri: str
    credentials: RegistryCredentials | None = None

    @field_validator("credentials", mode="before")
    @classmethod
    def _normalize_credentials(cls, value: object) -> object:
        if not isinstance(value, dict):
            return value

        normalized = dict(value)
        credential_type = normalized.get("type")
        if isinstance(credential_type, RegistryCredentialType):
            normalized["type"] = credential_type.value
        return normalized

    @model_validator(mode="after")
    def _validate_values(self) -> CreateTemplateParams:
        name = self.name.strip()
        uri = self.uri.strip()
        if not name:
            raise ValueError("name must be a non-empty string")
        if len(name) > 64:
            raise ValueError("name must be at most 64 characters")
        if name.startswith("system/"):
            raise ValueError("name must not start with 'system/'")
        if any(char.isspace() for char in name):
            raise ValueError("name must not contain whitespace")
        if not uri:
            raise ValueError("uri must be a non-empty string")
        if len(uri) > 500:
            raise ValueError("uri must be at most 500 characters")
        self.name = name
        self.uri = uri
        return self

    def to_payload(self) -> dict[str, object]:
        """Convert this object to an API request payload."""
        return self.model_dump(mode="json", exclude_none=True)

class RenameTemplateParams(BaseModel):
    """Validated template rename parameters."""
    model_config = ConfigDict(extra="forbid")

    name: str

    @model_validator(mode="after")
    def _validate_name(self) -> RenameTemplateParams:
        name = self.name.strip()
        if not name:
            raise ValueError("name must be a non-empty string")
        if len(name) > 64:
            raise ValueError("name must be at most 64 characters")
        if name.startswith("system/"):
            raise ValueError("name must not start with 'system/'")
        if any(char.isspace() for char in name):
            raise ValueError("name must not contain whitespace")
        self.name = name
        return self

    def to_payload(self) -> dict[str, str]:
        """Convert this object to an API request payload."""
        return {"name": self.name}
@dataclass(slots=True)
class ImageConfig:
    """Container image configuration metadata."""
    entrypoint: list[str] | None = None
    cmd: list[str] | None = None
    working_dir: str = ""
    user: str = ""
    env: dict[str, str] | None = None

    @classmethod
    def from_dict(cls, data: ImageConfigDict) -> ImageConfig:
        """Build an instance from a wire-format dictionary."""
        return cls(
            entrypoint=data.get("entrypoint"),
            cmd=data.get("cmd"),
            working_dir=data.get("working_dir", ""),
            user=data.get("user", ""),
            env=data.get("env"),
        )

@dataclass(slots=True)
class Template:
    """Template metadata returned by the API."""
    id: str
    name: str
    digest: str = ""
    image_config: ImageConfig | None = None
    is_system: bool = False
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: UploadTemplateResponseDict) -> Template:
        """Build an instance from a wire-format dictionary."""
        raw_id = data.get("id")  # type: ignore[arg-type]
        raw_name = data.get("name")  # type: ignore[arg-type]
        raw_digest = data.get("digest")  # type: ignore[arg-type]
        raw_created = data.get("created_at")  # type: ignore[arg-type]
        ic = data.get("image_config")
        raw_system = data.get("is_system")  # type: ignore[arg-type]
        return cls(
            id=raw_id if isinstance(raw_id, str) else "",
            name=raw_name if isinstance(raw_name, str) else "",
            digest=raw_digest if isinstance(raw_digest, str) else "",
            image_config=ImageConfig.from_dict(ic) if isinstance(ic, dict) else None,
            is_system=raw_system if isinstance(raw_system, bool) else False,
            created_at=raw_created if isinstance(raw_created, str) else "",
        )
