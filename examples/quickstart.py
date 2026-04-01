from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leap0 import CodeExecutionResult, Leap0, Leap0Config, Sandbox


def main() -> None:
    client = Leap0(Leap0Config())
    sandbox: Sandbox = client.sandboxes.create()

    try:
        result: CodeExecutionResult = sandbox.code_interpreter.execute(
            code="sum([10, 20, 30, 40]) / 4",
            language="python",
        )
        print("sandbox:", sandbox.id)
        print("result:", result.main_text)
    finally:
        sandbox.delete()
        client.close()


if __name__ == "__main__":
    main()
