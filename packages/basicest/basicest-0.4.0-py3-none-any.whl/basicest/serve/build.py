"""Logic for interacting with basicest-serve."""

from __future__ import annotations

import contextlib
import subprocess
import sys
import traceback
from collections.abc import Sequence
from pathlib import Path

from .utils import show_command, show_message


class Builder:
    def __init__(self, basicest_args, *, url_host):
        self.basicest_args = basicest_args
        self.uri = f"http://{url_host}"

    def __call__(self, *, changed_paths: Sequence[Path]):
        """Generate the documentation using ``basicest``."""
        if changed_paths:
            cwd = Path.cwd()
            rel_paths = []
            for changed_path in changed_paths[:5]:
                if not changed_path.exists():
                    continue
                with contextlib.suppress(ValueError):
                    changed_path = changed_path.relative_to(cwd)
                rel_paths.append(changed_path.as_posix())
            if rel_paths:
                show_message(f"Detected changes ({', '.join(rel_paths)})")
            show_message("Rebuilding...")

        py_args = ["-m", "basicest"] + self.basicest_args
        show_command(["python"] + py_args)
        try:
            subprocess.run([sys.executable] + py_args, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Basicest exited with exit code: {e.returncode}")
            print(
                "The server will continue serving the build folder, but the contents "
                "being served are no longer in sync with the documentation sources. "
                "Please fix the cause of the error above or press Ctrl+C to stop the "
                "server."
            )
        # Remind the user of the server URL for convenience.
        show_message(f"Serving on {self.uri}")
