from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leap0 import Leap0, Leap0Config


def main() -> None:
    client = Leap0(Leap0Config())
    sandbox = client.sandboxes.create()

    try:
        for event in client.code_interpreter.execute_stream(
            sandbox,
            code="import time\nfor i in range(3):\n    print(f'step {i}')\n    time.sleep(1)",
            language="python",
            timeout_ms=10_000,
        ):
            print(event)
    finally:
        client.sandboxes.delete(sandbox)
        client.close()


if __name__ == "__main__":
    main()
