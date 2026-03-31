from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leap0 import Leap0, Leap0Config, Leap0Error


def main() -> None:
    client = Leap0(Leap0Config())
    sandbox = client.sandboxes.create(template_name="system/desktop:v0.1.0")

    try:
        client.desktop.wait_until_ready(sandbox, timeout=60.0)
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
