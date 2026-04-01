from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leap0 import Leap0Client, ProcessResult, Sandbox


def main() -> None:
    client = Leap0Client()
    sandbox: Sandbox = client.sandboxes.create()

    try:
        result: ProcessResult = sandbox.process.execute(command="echo hello from leap0")
        print("sandbox:", sandbox.id)
        print("exit code:", result.exit_code)
        print("result:", result.result.strip())
    finally:
        sandbox.delete()
        client.close()


if __name__ == "__main__":
    main()
