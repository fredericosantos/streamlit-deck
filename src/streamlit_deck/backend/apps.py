import os
import sys
import glob
import subprocess
import hashlib
from PIL import Image
from io import BytesIO
from typing import Dict, Optional


def extract_macos_icon(app_path: str, size: tuple = (64, 64)) -> Optional[bytes]:
    """
    Extracts icon from a macOS .app bundle and returns it as bytes.
    """
    icon_path = os.path.join(app_path, "Contents", "Resources", "AppIcon.icns")

    if not os.path.exists(icon_path):
        # Try alternative icon names
        resources_dir = os.path.join(app_path, "Contents", "Resources")
        for file in os.listdir(resources_dir):
            if file.endswith(".icns"):
                icon_path = os.path.join(resources_dir, file)
                break
        else:
            return None

    try:
        # Open the .icns file with Pillow
        with Image.open(icon_path) as img:
            # Convert to PNG and resize
            img = img.convert("RGBA")
            img = img.resize(size, Image.Resampling.LANCZOS)

            # Save to bytes
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            return buffer.getvalue()
    except Exception as e:
        # print(f"Error extracting icon from {app_path}: {e}")
        return None


def get_cached_icon(app_path: str) -> Optional[bytes]:
    """Get icon from cache or extract and cache it."""
    cache_dir = os.path.expanduser("~/.streamlit_deck/cache/icons")
    os.makedirs(cache_dir, exist_ok=True)

    # Create cache key from app path
    cache_key = hashlib.md5(app_path.encode()).hexdigest()
    cache_file = os.path.join(cache_dir, f"{cache_key}.png")

    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            return f.read()

    # Extract and cache
    icon_bytes = extract_macos_icon(app_path)
    if icon_bytes:
        with open(cache_file, "wb") as f:
            f.write(icon_bytes)

    return icon_bytes


def get_installed_apps() -> Dict[str, Dict[str, str]]:
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

                        apps[name] = clean_cmd
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

                    # Extract icon
                    icon_bytes = get_cached_icon(full_path)

                    apps[name] = {"command": full_path, "icon_bytes": icon_bytes}

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
