from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leap0 import (
    DEFAULT_DESKTOP_TEMPLATE_NAME,
    DesktopDisplayInfo,
    Leap0,
    Leap0Config,
    Leap0Error,
    Sandbox,
)


def main() -> None:
    client = Leap0(Leap0Config())
    sandbox: Sandbox | None = None

    try:
        sandbox = client.sandboxes.create(template_name=DEFAULT_DESKTOP_TEMPLATE_NAME)
        sandbox.desktop.wait_until_ready(timeout=60.0)
        print("Desktop:", sandbox.desktop.desktop_url())

        display: DesktopDisplayInfo = sandbox.desktop.display_info()
        print("Display:", display)

        sandbox.desktop.move_pointer(x=display.width // 2, y=display.height // 2)
        sandbox.desktop.click(button=1)

        screenshot = sandbox.desktop.screenshot(image_format="png")
        Path("desktop-screenshot.png").write_bytes(screenshot)
        print("Saved screenshot to desktop-screenshot.png")
    finally:
        try:
            if sandbox is not None:
                sandbox.delete()
        except Leap0Error:
            pass
        finally:
            client.close()


if __name__ == "__main__":
    main()
