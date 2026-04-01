from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leap0 import Leap0, Leap0Config, Sandbox, StreamEvent


def main() -> None:
    client = Leap0(Leap0Config())
    sandbox: Sandbox = client.sandboxes.create()

    try:
        event: StreamEvent
        for event in sandbox.code_interpreter.execute_stream(
            code="import time\nfor i in range(3):\n    print(f'step {i}')\n    time.sleep(1)",
            language="python",
            timeout_ms=10_000,
        ):
            print(event)
    finally:
        sandbox.delete()
        client.close()


if __name__ == "__main__":
    main()
