from __future__ import annotations

from collections.abc import Iterator
from typing import Any, cast

import httpx

from ._transport import Transport
from ._utils.errors import intercept_errors
from ._utils.stream import iter_sse_events
from ._utils.url import sandbox_base_url
from .common.errors import Leap0Error
from .common.desktop import (
    DesktopDisplayInfo,
    DesktopDisplayInfoDict,
    DesktopHealth,
    DesktopHealthDict,
    DesktopPointerPosition,
    DesktopPointerPositionDict,
    DesktopProcessErrors,
    DesktopProcessErrorsDict,
    DesktopProcessLogs,
    DesktopProcessLogsDict,
    DesktopProcessRestart,
    DesktopProcessRestartDict,
    DesktopProcessStatus,
    DesktopProcessStatusDict,
    DesktopProcessStatusList,
    DesktopProcessStatusListDict,
    DesktopRecordingStatus,
    DesktopRecordingStatusDict,
    DesktopRecordingSummary,
    DesktopRecordingSummaryDict,
    DesktopWindow,
    DesktopWindowsDict,
)
from .common.sandbox import SandboxRef, sandbox_id_of


class DesktopClient:
    """Control a graphical Linux desktop inside a sandbox.

    Requires a sandbox created with the
    :data:`~leap0.constants.DEFAULT_DESKTOP_TEMPLATE_NAME`
    (``system/desktop:v0.1.0``) template.  Provides display info, screenshots,
    mouse/keyboard input, and screen recording.
    """

    def __init__(self, transport: Transport, *, sandbox_domain: str | None = None):
        self._transport = transport
        self._sandbox_domain = sandbox_domain.strip("/") if sandbox_domain else None

    def _request(
        self,
        method: str,
        sandbox: SandboxRef,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        expected_status: int | tuple[int, ...] = 200,
    ) -> httpx.Response:
        return self._transport.request_target(
            method,
            f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain)}{path}",
            params=params,
            json=json,
            expected_status=expected_status,
        )

    def _request_json(
        self,
        method: str,
        sandbox: SandboxRef,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        expected_status: int | tuple[int, ...] = 200,
    ) -> dict[str, Any]:
        return self._transport.request_target_json(
            method,
            f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain)}{path}",
            params=params,
            json=json,
            expected_status=expected_status,
        )

    def desktop_url(self, sandbox: SandboxRef) -> str:
        """Build the browser URL for the noVNC desktop viewer."""
        return f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain)}/"

    @intercept_errors("Failed to get display info: ")
    def display_info(self, sandbox: SandboxRef) -> DesktopDisplayInfo:
        """Get display information (display name, width, height)."""
        data: DesktopDisplayInfoDict = self._request_json("GET", sandbox, "/api/display")  # type: ignore[assignment]
        return DesktopDisplayInfo.from_dict(data)

    @intercept_errors("Failed to get screen info: ")
    def screen(self, sandbox: SandboxRef) -> DesktopDisplayInfo:
        """Get the current screen resolution."""
        data: DesktopDisplayInfoDict = self._request_json("GET", sandbox, "/api/display/screen")  # type: ignore[assignment]
        return DesktopDisplayInfo.from_dict(data)

    @intercept_errors("Failed to resize screen: ")
    def resize_screen(self, sandbox: SandboxRef, *, width: int, height: int) -> DesktopDisplayInfo:
        """Resize the virtual display (width: 320-7680, height: 320-4320)."""
        data: DesktopDisplayInfoDict = self._request_json(  # type: ignore[assignment]
            "POST",
            sandbox,
            "/api/display/screen",
            json={"width": width, "height": height},
        )
        return DesktopDisplayInfo.from_dict(data)

    @intercept_errors("Failed to list windows: ")
    def windows(self, sandbox: SandboxRef) -> list[DesktopWindow]:
        """List all open windows on the desktop."""
        data: DesktopWindowsDict = self._request_json("GET", sandbox, "/api/display/windows")  # type: ignore[assignment]
        return [DesktopWindow.from_dict(item) for item in data.get("items", [])]

    @intercept_errors("Failed to take screenshot: ")
    def screenshot(
        self,
        sandbox: SandboxRef,
        *,
        image_format: str | None = None,
        quality: int | None = None,
        x: int | None = None,
        y: int | None = None,
        width: int | None = None,
        height: int | None = None,
    ) -> bytes:
        """Take a screenshot and return the image as bytes.

        Args:
            sandbox: Sandbox ID or object.
            image_format: ``"png"``, ``"jpg"``, or ``"jpeg"`` (default ``"png"``).
            quality: JPEG quality (1-100).
            x: Left edge of capture region.
            y: Top edge of capture region.
            width: Region width in pixels.
            height: Region height in pixels.
        """
        params: dict[str, Any] = {}
        if image_format is not None:
            params["format"] = image_format
        if quality is not None:
            params["quality"] = quality
        if x is not None:
            params["x"] = x
        if y is not None:
            params["y"] = y
        if width is not None:
            params["width"] = width
        if height is not None:
            params["height"] = height
        response = self._request("GET", sandbox, "/api/screenshot", params=params or None)
        return response.content

    @intercept_errors("Failed to take screenshot: ")
    def screenshot_region(
        self,
        sandbox: SandboxRef,
        *,
        x: int,
        y: int,
        width: int,
        height: int,
        image_format: str | None = None,
        quality: int | None = None,
    ) -> bytes:
        """Take a screenshot of a specific region and return the image as bytes."""
        payload: dict[str, Any] = {"x": x, "y": y, "width": width, "height": height}
        if image_format is not None:
            payload["format"] = image_format
        if quality is not None:
            payload["quality"] = quality
        response = self._request("POST", sandbox, "/api/screenshot/region", json=payload)
        return response.content

    @intercept_errors("Failed to get pointer position: ")
    def pointer_position(self, sandbox: SandboxRef) -> DesktopPointerPosition:
        """Get the current mouse pointer position."""
        data: DesktopPointerPositionDict = self._request_json("GET", sandbox, "/api/input/position")  # type: ignore[assignment]
        return DesktopPointerPosition.from_dict(data)

    @intercept_errors("Failed to move pointer: ")
    def move_pointer(self, sandbox: SandboxRef, *, x: int, y: int) -> DesktopPointerPosition:
        """Move the mouse pointer to the given coordinates."""
        data: DesktopPointerPositionDict = self._request_json("POST", sandbox, "/api/input/move", json={"x": x, "y": y})  # type: ignore[assignment]
        return DesktopPointerPosition.from_dict(data)

    @intercept_errors("Failed to click: ")
    def click(
        self,
        sandbox: SandboxRef,
        *,
        x: int | None = None,
        y: int | None = None,
        button: int | None = None,
    ) -> DesktopPointerPosition:
        """Click the mouse. Clicks at the current position if coordinates are omitted.

        Args:
            sandbox: Sandbox ID or object.
            x: X coordinate.
            y: Y coordinate.
            button: 1=left, 2=middle, 3=right (default 1).
        """
        payload: dict[str, Any] = {}
        if x is not None:
            payload["x"] = x
        if y is not None:
            payload["y"] = y
        if button is not None:
            payload["button"] = button
        data: DesktopPointerPositionDict = self._request_json("POST", sandbox, "/api/input/click", json=payload)  # type: ignore[assignment]
        return DesktopPointerPosition.from_dict(data)

    @intercept_errors("Failed to drag: ")
    def drag(
        self,
        sandbox: SandboxRef,
        *,
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int,
        button: int | None = None,
    ) -> DesktopPointerPosition:
        """Drag from one position to another."""
        payload: dict[str, Any] = {
            "from_x": from_x,
            "from_y": from_y,
            "to_x": to_x,
            "to_y": to_y,
        }
        if button is not None:
            payload["button"] = button
        data: DesktopPointerPositionDict = self._request_json("POST", sandbox, "/api/input/drag", json=payload)  # type: ignore[assignment]
        return DesktopPointerPosition.from_dict(data)

    @intercept_errors("Failed to scroll: ")
    def scroll(self, sandbox: SandboxRef, *, direction: str, amount: int | None = None) -> DesktopPointerPosition:
        """Scroll the mouse wheel.

        Args:
            sandbox: Sandbox ID or object.
            direction: ``"up"``, ``"down"``, ``"left"``, or ``"right"``.
            amount: Number of scroll steps (1-100, default 1).
        """
        payload: dict[str, Any] = {"direction": direction}
        if amount is not None:
            payload["amount"] = amount
        data: DesktopPointerPositionDict = self._request_json("POST", sandbox, "/api/input/scroll", json=payload)  # type: ignore[assignment]
        return DesktopPointerPosition.from_dict(data)

    @intercept_errors("Failed to type text: ")
    def type_text(self, sandbox: SandboxRef, *, text: str) -> bool:
        """Type text using simulated keyboard input (max 50,000 characters)."""
        data = self._request_json("POST", sandbox, "/api/input/type", json={"text": text})
        return bool(data.get("ok", False))

    @intercept_errors("Failed to press key: ")
    def press_key(self, sandbox: SandboxRef, *, key: str) -> bool:
        """Press a single key by X11 keysym name (e.g. ``"Return"``, ``"Escape"``)."""
        data = self._request_json("POST", sandbox, "/api/input/press", json={"key": key})
        return bool(data.get("ok", False))

    @intercept_errors("Failed to press hotkey: ")
    def hotkey(self, sandbox: SandboxRef, *, keys: list[str]) -> bool:
        """Press multiple keys simultaneously (e.g. ``["Control_L", "c"]``)."""
        data = self._request_json("POST", sandbox, "/api/input/hotkey", json={"keys": keys})
        return bool(data.get("ok", False))

    @intercept_errors("Failed to get recording status: ")
    def recording_status(self, sandbox: SandboxRef) -> DesktopRecordingStatus:
        """Get the current screen recording status."""
        data: DesktopRecordingStatusDict = self._request_json("GET", sandbox, "/api/recording")  # type: ignore[assignment]
        return DesktopRecordingStatus.from_dict(data)

    @intercept_errors("Failed to start recording: ")
    def start_recording(self, sandbox: SandboxRef) -> DesktopRecordingStatus:
        """Start recording the screen. Returns 409 if a recording is already active."""
        data: DesktopRecordingStatusDict = self._request_json("POST", sandbox, "/api/recording/start", expected_status=201)  # type: ignore[assignment]
        return DesktopRecordingStatus.from_dict(data)

    @intercept_errors("Failed to stop recording: ")
    def stop_recording(self, sandbox: SandboxRef) -> DesktopRecordingStatus:
        """Stop the active screen recording."""
        data: DesktopRecordingStatusDict = self._request_json("POST", sandbox, "/api/recording/stop")  # type: ignore[assignment]
        return DesktopRecordingStatus.from_dict(data)

    @intercept_errors("Failed to list recordings: ")
    def recordings(self, sandbox: SandboxRef) -> list[DesktopRecordingSummary]:
        """List all screen recordings."""
        raw = self._request_json("GET", sandbox, "/api/recordings")
        items: list[DesktopRecordingSummaryDict] = raw.get("items", [])  # type: ignore[assignment]
        return [DesktopRecordingSummary.from_dict(item) for item in items]

    @intercept_errors("Failed to get recording: ")
    def get_recording(self, sandbox: SandboxRef, recording_id: str) -> DesktopRecordingSummary:
        """Get details for a single recording."""
        data: DesktopRecordingSummaryDict = self._request_json("GET", sandbox, f"/api/recordings/{recording_id}")  # type: ignore[assignment]
        return DesktopRecordingSummary.from_dict(data)

    @intercept_errors("Failed to download recording: ")
    def download_recording(self, sandbox: SandboxRef, recording_id: str) -> bytes:
        """Download a recording as MP4 bytes."""
        response = self._request("GET", sandbox, f"/api/recordings/{recording_id}/download")
        return response.content

    @intercept_errors("Failed to delete recording: ")
    def delete_recording(self, sandbox: SandboxRef, recording_id: str) -> None:
        """Delete a recording. Cannot delete an active recording."""
        self._request("DELETE", sandbox, f"/api/recordings/{recording_id}", expected_status=204)

    @intercept_errors("Failed to check desktop health: ")
    def health(self, sandbox: SandboxRef) -> DesktopHealth:
        """Check the health of the desktop environment."""
        data: DesktopHealthDict = self._request_json("GET", sandbox, "/api/healthz")  # type: ignore[assignment]
        return DesktopHealth.from_dict(data)

    @intercept_errors("Failed to get process status: ")
    def process_status(self, sandbox: SandboxRef) -> DesktopProcessStatusList:
        """Get the status of all desktop processes (xvfb, xfce4, x11vnc, novnc)."""
        data: DesktopProcessStatusListDict = self._request_json("GET", sandbox, "/api/status")  # type: ignore[assignment]
        return DesktopProcessStatusList.from_dict(data)

    @intercept_errors("Failed to get process: ")
    def get_process(self, sandbox: SandboxRef, process_name: str) -> DesktopProcessStatus:
        """Get the status of a single desktop process by name."""
        data: DesktopProcessStatusDict = self._request_json("GET", sandbox, f"/api/process/{process_name}/status")  # type: ignore[assignment]
        return DesktopProcessStatus.from_dict(data)

    @intercept_errors("Failed to restart process: ")
    def restart_process(self, sandbox: SandboxRef, process_name: str) -> DesktopProcessRestart:
        """Restart a desktop process."""
        data: DesktopProcessRestartDict = self._request_json("POST", sandbox, f"/api/process/{process_name}/restart")  # type: ignore[assignment]
        return DesktopProcessRestart.from_dict(data)

    @intercept_errors("Failed to get process logs: ")
    def process_logs(self, sandbox: SandboxRef, process_name: str) -> DesktopProcessLogs:
        """Get stdout logs for a desktop process."""
        data: DesktopProcessLogsDict = self._request_json("GET", sandbox, f"/api/process/{process_name}/logs")  # type: ignore[assignment]
        return DesktopProcessLogs.from_dict(data)

    @intercept_errors("Failed to get process errors: ")
    def process_errors(self, sandbox: SandboxRef, process_name: str) -> DesktopProcessErrors:
        """Get stderr logs for a desktop process."""
        data: DesktopProcessErrorsDict = self._request_json("GET", sandbox, f"/api/process/{process_name}/errors")  # type: ignore[assignment]
        return DesktopProcessErrors.from_dict(data)

    @intercept_errors("Failed to stream status: ")
    def status_stream(self, sandbox: SandboxRef) -> Iterator[DesktopProcessStatusList]:
        """Subscribe to a live SSE stream of process status updates."""
        url = f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain)}/api/status/stream"
        response = self._transport.stream("GET", url)
        try:
            for event in iter_sse_events(response.iter_lines()):
                if isinstance(event, str):
                    raise Leap0Error("Desktop status stream error", body=event)
                yield DesktopProcessStatusList.from_dict(cast(DesktopProcessStatusListDict, event))
        finally:
            response.close()
