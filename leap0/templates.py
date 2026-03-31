from __future__ import annotations

from typing import Any

from ._transport import Transport
from ._utils.errors import intercept_errors
from .common.template import RegistryCredentialsDict, Template, UploadTemplateResponseDict


class TemplatesClient:
    """Create, rename, and delete sandbox templates.

    A template is a container image that has been converted into a sandbox
    root filesystem.  Sandboxes are always created from a template.
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
        """
        payload: dict[str, Any] = {"name": name, "uri": uri}
        if credentials is not None:
            payload["credentials"] = credentials
        data: UploadTemplateResponseDict = self._transport.request_json("POST", "/v1/template", json=payload, expected_status=201)  # type: ignore[assignment]
        return Template.from_dict(data)

    @intercept_errors("Failed to rename template: ")
    def rename(self, template_id: str, *, name: str) -> None:
        """Rename an existing template.

        Args:
            template_id: ID of the template to rename.
            name: New template name.
        """
        self._transport.request("PATCH", f"/v1/template/{template_id}", json={"name": name}, expected_status=204)

    @intercept_errors("Failed to delete template: ")
    def delete(self, template_id: str) -> None:
        """Delete a template by ID."""
        self._transport.request("DELETE", f"/v1/template/{template_id}", expected_status=204)
