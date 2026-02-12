"""
Linux-specific app detection and launching for Streamlit Deck.
"""

import os
import glob
import subprocess
import shlex
from typing import Dict
from ..base.apps import BaseApps


class LinuxApps(BaseApps):
    def get_installed_apps(self) -> Dict[str, Dict[str, str]]:
        """
        Returns a dictionary of {App Name: {'command': str, 'icon_bytes': bytes}}
        Detected from .desktop files on Linux.
        """

        apps = {}

        paths = [
            "/usr/share/applications",
            os.path.expanduser("~/.local/share/applications"),
        ]

        for path in paths:
            if not os.path.exists(path):
                continue

            for file in glob.glob(os.path.join(path, "*.desktop")):
                try:
                    name = None
                    exec_cmd = None
                    icon_path = None
                    # Read only first few lines usually sufficient, but we parse full file carefully
                    with open(file, "r", errors="ignore") as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("Name=") and not name:
                                name = line.split("=", 1)[1]
                            elif line.startswith("Exec=") and not exec_cmd:
                                exec_cmd = line.split("=", 1)[1]
                            elif line.startswith("Icon=") and not icon_path:
                                icon_path = line.split("=", 1)[1]

                            if name and exec_cmd:
                                break

                    if name and exec_cmd:
                        # Clean up exec command (remove %f, %u, etc placeholders)
                        cmd_parts = shlex.split(exec_cmd)
                        clean_cmd = [
                            part for part in cmd_parts if not part.startswith("%")
                        ]
                        command = shlex.join(clean_cmd)

                        # Try to load icon if specified
                        icon_bytes = None
                        if icon_path:
                            # Check for SVG first, then PNG
                            for ext in [".svg", ".png", ""]:
                                candidate_path = icon_path + ext if ext else icon_path
                                if os.path.exists(candidate_path):
                                    try:
                                        with open(candidate_path, "rb") as f:
                                            icon_bytes = f.read()
                                        break
                                    except Exception:
                                        continue

                        apps[name] = {
                            "command": command,
                            "icon_bytes": icon_bytes,
                        }
                except Exception:
                    continue

        return dict(sorted(apps.items()))

    def launch_app(self, command: str) -> str:
        """
        Launches the application on Linux.
        """

        try:
            # Run command directly with shlex split
            cmd_list = shlex.split(command)
            subprocess.Popen(cmd_list, start_new_session=True)
            return f"Launched command: {command}"
        except Exception as e:
            return f"Error launching app: {e}"
