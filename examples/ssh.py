from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leap0 import Leap0, Leap0Config, Sandbox, SshAccess, SshValidation


def main() -> None:
    client = Leap0(Leap0Config())
    sandbox: Sandbox = client.sandboxes.create()

    try:
        access: SshAccess = sandbox.ssh.create_access()
        print("ssh command:", access.ssh_command)

        validation: SshValidation = sandbox.ssh.validate_access(
            access_id=access.id,
            password=access.password,
        )
        print("ssh valid:", validation.valid)
    finally:
        sandbox.delete()
        client.close()


if __name__ == "__main__":
    main()
