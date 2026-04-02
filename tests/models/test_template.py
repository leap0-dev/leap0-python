from __future__ import annotations

import pytest

from leap0.models.template import (
    AwsRegistryCredentials,
    AzureRegistryCredentials,
    BasicRegistryCredentials,
    CreateTemplateParams,
    GcpRegistryCredentials,
    ImageConfig,
    RegistryCredentialType,
    Template,
)


class TestImageConfig:
    def test_full(self):
        c = ImageConfig.from_dict({"entrypoint": ["/bin/sh"], "cmd": ["-c", "echo hi"],
                                   "working_dir": "/workspace", "user": "appuser", "env": {"PATH": "/usr/bin"}})
        assert c.entrypoint == ["/bin/sh"]
        assert c.user == "appuser"

    def test_null_lists(self):
        c = ImageConfig.from_dict({"entrypoint": None, "cmd": None})
        assert c.entrypoint is None
        assert c.cmd is None


class TestTemplate:
    def test_full(self):
        t = Template.from_dict({"id": "tpl-1", "name": "my-template", "digest": "sha256:abc",
                                "image_config": {"entrypoint": ["/bin/sh"]}, "is_system": False, "created_at": "2025-01-01"})
        assert t.image_config.entrypoint == ["/bin/sh"]

    def test_null_image_config(self):
        t = Template.from_dict({"id": "tpl-2", "name": "t2", "digest": "", "image_config": None,
                                "is_system": True, "created_at": ""})
        assert t.image_config is None
        assert t.is_system is True


class TestCreateTemplateParams:
    def test_accepts_basic_registry_credentials(self):
        params = CreateTemplateParams(
            name="private-basic",
            uri="registry.example.com/org/app:latest",
            credentials={
                "type": RegistryCredentialType.BASIC,
                "username": "my-user",
                "password": "my-password",
            },
        )
        assert isinstance(params.credentials, BasicRegistryCredentials)
        assert params.credentials.type == "basic"

    def test_accepts_aws_registry_credentials(self):
        params = CreateTemplateParams(
            name="private-aws",
            uri="123456789012.dkr.ecr.us-east-1.amazonaws.com/app:latest",
            credentials={
                "type": RegistryCredentialType.AWS,
                "aws_access_key_id": "AKIA...",
                "aws_secret_access_key": "secret",
                "aws_region": "us-east-1",
            },
        )
        assert isinstance(params.credentials, AwsRegistryCredentials)
        assert params.credentials.type == "aws"

    def test_accepts_gcp_registry_credentials(self):
        params = CreateTemplateParams(
            name="private-gcp",
            uri="us-docker.pkg.dev/project/repo/app:latest",
            credentials={
                "type": RegistryCredentialType.GCP,
                "gcp_service_account_json": '{"type":"service_account"}',
            },
        )
        assert isinstance(params.credentials, GcpRegistryCredentials)
        assert params.credentials.type == "gcp"

    def test_accepts_azure_registry_credentials(self):
        params = CreateTemplateParams(
            name="private-azure",
            uri="registry.azurecr.io/app:latest",
            credentials={
                "type": RegistryCredentialType.AZURE,
                "azure_client_id": "client-id",
                "azure_client_secret": "client-secret",
                "azure_tenant_id": "tenant-id",
            },
        )
        assert isinstance(params.credentials, AzureRegistryCredentials)
        assert params.credentials.type == "azure"

    def test_rejects_incomplete_basic_registry_credentials(self):
        with pytest.raises(ValueError, match="password"):
            CreateTemplateParams(
                name="private-basic",
                uri="registry.example.com/org/app:latest",
                credentials={
                    "type": RegistryCredentialType.BASIC,
                    "username": "my-user",
                },
            )
