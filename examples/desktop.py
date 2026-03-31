from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leap0 import Leap0, Leap0Client, Leap0Config, Leap0Error
from leap0.common.sandbox import SandboxRef


def wait_for_desktop(client: Leap0Client, sandbox: SandboxRef, *, timeout_seconds: float = 60.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        sandbox_status = client.sandboxes.get(sandbox)
        if sandbox_status.state == "running":
            try:
                health = client.desktop.health(sandbox)
            except Leap0Error:
                pass
            else:
                if health.ok and health.state == "ready":
                    return
        time.sleep(0.25)
    raise TimeoutError(f"Sandbox {sandbox} did not become ready within {timeout_seconds:.0f}s")


def main() -> None:
    client = Leap0(Leap0Config())
    sandbox = client.sandboxes.create(template_name="system/desktop:v0.1.0")

    try:
        wait_for_desktop(client, sandbox)
        print("Desktop:", client.desktop.desktop_url(sandbox))

        display = client.desktop.display_info(sandbox)
        print("Display:", display)

        client.desktop.move_pointer(sandbox, x=display.width // 2, y=display.height // 2)
        client.desktop.click(sandbox, button=1)

        screenshot = client.desktop.screenshot(sandbox, image_format="png")
        Path("desktop-screenshot.png").write_bytes(screenshot)
        print("Saved screenshot to desktop-screenshot.png")
    finally:
        try:
            client.sandboxes.delete(sandbox)
        except Leap0Error:
            pass
        finally:
            client.close()


if __name__ == "__main__":
    main()
