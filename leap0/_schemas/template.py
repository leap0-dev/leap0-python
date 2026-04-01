from __future__ import annotations

from typing import TypedDict
from typing_extensions import Literal, NotRequired, Required, TypeAlias

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.template import RegistryCredentialType

class BasicRegistryCredentialsDict(TypedDict, total=False):
    """Wire schema for basic registry credentials."""
    type: Required[Literal[RegistryCredentialType.BASIC, "basic"]]
    username: Required[str]
    password: Required[str]

class AwsRegistryCredentialsDict(TypedDict, total=False):
    """Wire schema for AWS registry credentials."""
    type: Required[Literal[RegistryCredentialType.AWS, "aws"]]
    aws_access_key_id: Required[str]
    aws_secret_access_key: Required[str]
    aws_region: NotRequired[str]

class GcpRegistryCredentialsDict(TypedDict, total=False):
    """Wire schema for GCP registry credentials."""
    type: Required[Literal[RegistryCredentialType.GCP, "gcp"]]
    gcp_service_account_json: Required[str]

class AzureRegistryCredentialsDict(TypedDict, total=False):
    """Wire schema for Azure registry credentials."""
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
    """Wire schema for image configuration."""
    entrypoint: list[str] | None
    cmd: list[str] | None
    working_dir: str
    user: str
    env: dict[str, str] | None

class UploadTemplateResponseDict(TypedDict):
    """Wire schema for template upload responses."""
    id: str
    name: str
    digest: str
    image_config: ImageConfigDict | None
    is_system: bool
    created_at: str
