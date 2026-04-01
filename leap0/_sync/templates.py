from __future__ import annotations

from typing import cast

from ._transport import Transport
from .._utils.errors import intercept_errors
from ..models.template import (
    CreateTemplateParams,
    RegistryCredentialsDict,
    RenameTemplateParams,
    Template,
)
from .._schemas.template import UploadTemplateResponseDict


class TemplatesClient:
    """Create, rename, and delete sandbox templates.
    
        A template is a container image that has been converted into a sandbox
        root filesystem.  Sandboxes are always created from a template.
    
        Example:
            ```python
            template = client.templates.create(
                name="my-template",
                uri="docker.io/library/python:3.12",
            )
            print(template.id)
            ```
        
    Attributes:
        None.
    """

    def __init__(self, transport: Transport):
        self._transport = transport

    @intercept_errors("Failed to create template: ")
    def create(self, *, name: str, uri: str, credentials: RegistryCredentialsDict | None = None) -> Template:
        """Upload a new template from a container image URI.

        Args:
            name: Template name. Must not start with ``system/`` or contain whitespace.
            uri: Container image URI to pull and convert (e.g. ``docker.io/library/python:3.12``).
            credentials: Optional registry credentials for private images.
                Supports basic, AWS, GCP, and Azure authentication.

        Returns:
            Template: Uploaded template metadata.
        """
        payload = CreateTemplateParams(name=name, uri=uri, credentials=credentials).to_payload()
        data = cast(UploadTemplateResponseDict, self._transport.request_json("POST", "/v1/template", json=payload, expected_status=201))
        return Template.from_dict(data)

    @intercept_errors("Failed to rename template: ")
    def rename(self, template_id: str, *, name: str, http_timeout: float | None = None) -> None:
        """Rename an existing template.

        Args:
            template_id: ID of the template to rename.
            name: New template name.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        """
        payload = RenameTemplateParams(name=name).to_payload()
        self._transport.request("PATCH", f"/v1/template/{template_id}", json=payload, expected_status=204, timeout=http_timeout)

    @intercept_errors("Failed to delete template: ")
    def delete(self, template_id: str, http_timeout: float | None = None) -> None:
        """Delete a template by ID.

        Args:
            template_id: ID of the template to delete.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        """
        self._transport.request("DELETE", f"/v1/template/{template_id}", expected_status=204, timeout=http_timeout)
