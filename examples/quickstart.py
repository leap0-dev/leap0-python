from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leap0 import Leap0, Leap0Config


def main() -> None:
    client = Leap0(Leap0Config())
    sandbox = client.sandboxes.create()

    try:
        result = client.code_interpreter.execute(
            sandbox,
            code="sum([10, 20, 30, 40]) / 4",
            language="python",
        )
        print("sandbox:", sandbox.id)
        print("result:", result.main_text)
    finally:
        client.sandboxes.delete(sandbox)
        client.close()


if __name__ == "__main__":
    main()
