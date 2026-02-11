import os
import sys
import glob
import subprocess
from typing import Dict


def get_installed_apps() -> Dict[str, str]:
    """
    Returns a dictionary of {App Name: Execution Command/Path}
    """
    apps = {}

    if sys.platform == "linux":
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
                    # Read only first few lines usually sufficient, but we parse full file carefully
                    with open(file, "r", errors="ignore") as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("Name=") and not name:
                                name = line.split("=", 1)[1]
                            elif line.startswith("Exec=") and not exec_cmd:
                                exec_cmd = line.split("=", 1)[1]

                            if name and exec_cmd:
                                break

                    if name and exec_cmd:
                        # Clean up exec command (remove %f, %u, etc placeholders)
                        cmd_parts = exec_cmd.split()
                        clean_cmd = []
                        for part in cmd_parts:
                            if not part.startswith("%"):
                                clean_cmd.append(part)

                        apps[name] = " ".join(clean_cmd)
                except Exception:
                    continue

    elif sys.platform == "darwin":  # macOS
        paths = ["/Applications", os.path.expanduser("~/Applications")]

        for path in paths:
            if not os.path.exists(path):
                continue

            for item in os.listdir(path):
                if item.endswith(".app"):
                    name = item[:-4]  # Remove .app
                    full_path = os.path.join(path, item)
                    apps[name] = full_path

    return dict(sorted(apps.items()))


def launch_app(command: str) -> str:
    """
    Launches the application.
    """
    try:
        if sys.platform == "darwin":
            subprocess.Popen(["open", command])
            return f"Opened app: {os.path.basename(command)}"
        else:
            # Linux/Other: Run command directly
            # Use setsid to detach process
            subprocess.Popen(command, shell=True, start_new_session=True)
            return f"Launched command: {command}"
    except Exception as e:
        return f"Error launching app: {e}"
