from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leap0 import Leap0Client, Sandbox, SshAccess, SshValidation


def main() -> None:
    client = Leap0Client()
    sandbox: Sandbox = client.sandboxes.create()

    try:
        access: SshAccess = sandbox.ssh.create_access()
        print("ssh command:", access.ssh_command)

        validation: SshValidation = sandbox.ssh.validate_access(
            id=access.id,
            password=access.password,
        )
        print("ssh valid:", validation.valid)
        rotated: SshAccess = sandbox.ssh.regenerate_access(id=access.id)
        print("rotated ssh command:", rotated.ssh_command)
    finally:
        sandbox.delete()
        client.close()


if __name__ == "__main__":
    main()
