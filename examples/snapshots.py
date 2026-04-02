from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leap0 import Leap0Client, Sandbox, Snapshot


def main() -> None:
    client = Leap0Client()
    sandbox: Sandbox = client.sandboxes.create()

    try:
        sandbox.filesystem.write_file(path="/workspace/checkpoint.txt", content="before snapshot\n")

        snapshot: Snapshot = client.snapshots.create(sandbox, name="example-checkpoint")
        print("snapshot:", snapshot.id)

        restored: Sandbox = client.snapshots.resume(snapshot_name=snapshot.name)
        try:
            content = restored.filesystem.read_file(path="/workspace/checkpoint.txt")
            print("restored file:", content.strip())
        finally:
            restored.delete()
    finally:
        sandbox.delete()
        client.close()


if __name__ == "__main__":
    main()
