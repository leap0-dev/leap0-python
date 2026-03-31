from __future__ import annotations

from typing import Any

import httpx

from .common.config import DEFAULT_CLIENT_TIMEOUT
from .common.errors import raise_api_error


class Transport:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: float = DEFAULT_CLIENT_TIMEOUT,
        auth_header: str = "authorization",
        bearer: bool = True,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.auth_header = auth_header
        self.bearer = bearer
        self._client = httpx.Client(timeout=timeout)

    @property
    def auth_value(self) -> str:
        if self.bearer and not self.api_key.lower().startswith("bearer "):
            return f"Bearer {self.api_key}"
        return self.api_key

    def close(self) -> None:
        self._client.close()

    def headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        headers = {self.auth_header: self.auth_value}
        if extra:
            headers.update(extra)
        return headers

    def _expected(self, expected_status: int | tuple[int, ...]) -> tuple[int, ...]:
        return (expected_status,) if isinstance(expected_status, int) else expected_status

    def _target_url(self, target: str) -> str:
        if target.startswith("https://") or target.startswith("http://"):
            return target
        return f"{self.base_url}{target}"

    def _check_response(self, response: httpx.Response, method: str, target: str, expected_status: int | tuple[int, ...]) -> httpx.Response:
        expected = self._expected(expected_status)
        if response.status_code not in expected:
            raise_api_error(
                response.status_code,
                f"Request failed: {method} {target}",
                body=response.text,
                headers=dict(response.headers),
            )
        return response

    def _request(
        self,
        method: str,
        target: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        content: Any = None,
        files: Any = None,
        headers: dict[str, str] | None = None,
        expected_status: int | tuple[int, ...] = 200,
        timeout: float | None = None,
    ) -> httpx.Response:
        actual_target = self._target_url(target)
        response = self._client.request(
            method,
            actual_target,
            params=params,
            json=json,
            content=content,
            files=files,
            headers=self.headers(headers),
            timeout=timeout or self.timeout,
        )
        return self._check_response(response, method, target, expected_status)

    def _stream(
        self,
        method: str,
        target: str,
        *,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        effective = timeout if timeout is not None else self.timeout
        timeout_dict = {"connect": effective, "read": effective, "write": effective, "pool": effective}
        request = self._client.build_request(
            method,
            self._target_url(target),
            json=json,
            headers=self.headers(),
            extensions={"timeout": timeout_dict},
        )
        response = self._client.send(request, stream=True)
        if response.status_code >= 400:
            body = response.read().decode("utf-8", errors="replace")
            hdrs = dict(response.headers)
            response.close()
            raise_api_error(response.status_code, f"Request failed: {method} {target}", body=body, headers=hdrs)
        return response

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        content: Any = None,
        files: Any = None,
        headers: dict[str, str] | None = None,
        expected_status: int | tuple[int, ...] = 200,
        timeout: float | None = None,
    ) -> httpx.Response:
        url = f"{self.base_url}{path}"
        actual_headers = self.headers(headers)
        response = self._client.request(
            method,
            url,
            params=params,
            json=json,
            content=content,
            files=files,
            headers=actual_headers,
            timeout=timeout or self.timeout,
        )
        return self._check_response(response, method, path, expected_status)

    def request_json(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        content: Any = None,
        headers: dict[str, str] | None = None,
        expected_status: int | tuple[int, ...] = 200,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Like request() but parses and returns the JSON body as a dict."""
        resp = self.request(
            method,
            path,
            params=params,
            json=json,
            content=content,
            headers=headers,
            expected_status=expected_status,
            timeout=timeout,
        )
        return resp.json()

    def request_target(
        self,
        method: str,
        target: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        expected_status: int | tuple[int, ...] = 200,
    ) -> httpx.Response:
        """Send a request to an absolute URL (e.g. sandbox-domain URLs)."""
        return self._request(method, target, params=params, json=json, expected_status=expected_status)

    def request_target_json(
        self,
        method: str,
        target: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        expected_status: int | tuple[int, ...] = 200,
    ) -> dict[str, Any]:
        """Send a request to an absolute URL and return parsed JSON."""
        resp = self._request(method, target, params=params, json=json, expected_status=expected_status)
        return resp.json()

    def stream(self, method: str, target: str, *, json: dict[str, Any] | None = None, timeout: float | None = None) -> httpx.Response:
        return self._stream(method, target, json=json, timeout=timeout)
