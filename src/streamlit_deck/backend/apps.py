import os
import sys
import glob
import subprocess
import hashlib
from PIL import Image
from io import BytesIO
from typing import Dict, Optional

# macOS specific imports
if sys.platform == "darwin":
    from AppKit import NSWorkspace
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGWindowListOptionOnScreenOnly,
        kCGNullWindowID,
    )


def extract_macos_icon(app_path: str, size: tuple = (64, 64)) -> Optional[bytes]:
    """
    Extracts icon from a macOS .app bundle and returns it as bytes.
    Prefers SVG if available, falls back to PNG from .icns
    """
    resources_dir = os.path.join(app_path, "Contents", "Resources")

    if not os.path.exists(resources_dir):
        return None

    # First, try to find SVG files
    for file in os.listdir(resources_dir):
        if file.lower().endswith(".svg"):
            svg_path = os.path.join(resources_dir, file)
            try:
                with open(svg_path, "rb") as f:
                    return f.read()
            except Exception:
                continue

    # Fall back to .icns extraction
    icon_path = os.path.join(resources_dir, "AppIcon.icns")

    if not os.path.exists(icon_path):
        # Try alternative icon names
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
    except Exception:
        return None


def get_cached_icon(app_path: str) -> Optional[bytes]:
    """Get icon from cache or extract and cache it."""
    cache_dir = os.path.expanduser("~/.streamlit_deck/cache/icons")
    os.makedirs(cache_dir, exist_ok=True)

    # Create cache key from app path
    cache_key = hashlib.md5(app_path.encode()).hexdigest()

    # Check for both SVG and PNG cache files
    svg_cache_file = os.path.join(cache_dir, f"{cache_key}.svg")
    png_cache_file = os.path.join(cache_dir, f"{cache_key}.png")

    # Prefer SVG cache
    if os.path.exists(svg_cache_file):
        with open(svg_cache_file, "rb") as f:
            return f.read()

    # Fall back to PNG cache
    if os.path.exists(png_cache_file):
        with open(png_cache_file, "rb") as f:
            return f.read()

    # Extract and cache
    icon_bytes = extract_macos_icon(app_path)
    if icon_bytes:
        # Determine if it's SVG (starts with <?xml or <svg) or PNG
        if icon_bytes.startswith(b"<?xml") or icon_bytes.startswith(b"<svg"):
            cache_file = svg_cache_file
        else:
            cache_file = png_cache_file

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
                        cmd_parts = exec_cmd.split()
                        clean_cmd = []
                        for part in cmd_parts:
                            if not part.startswith("%"):
                                clean_cmd.append(part)

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

                        apps[name] = {"command": clean_cmd, "icon_bytes": icon_bytes}
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


def get_open_windows() -> dict:
    """
    Get list of open windows on macOS using Quartz.
    Returns dict with 'windows' list and 'debug' string
    """
    debug_messages = []

    if sys.platform != "darwin":
        return {"windows": [], "debug": "Not macOS"}

    windows_info = []

    try:
        debug_messages.append("Getting window list with Quartz...")
        # Get window list
        window_list = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly, kCGNullWindowID
        )
        debug_messages.append(f"Found {len(window_list)} windows")

        for window in window_list:
            owner_name = window.get("kCGWindowOwnerName")
            window_name = window.get("kCGWindowName", "N/A")
            bounds = window.get("kCGWindowBounds")

            if owner_name:
                debug_messages.append(
                    f"Window: {window_name}, App: {owner_name}, Bounds: {bounds}"
                )
                windows_info.append(
                    {
                        "title": window_name,
                        "app_name": owner_name,
                        "bounds": bounds,
                    }
                )

    except Exception as e:
        debug_messages.append(f"Error: {e}")
        # Gracefully handle any API errors
        pass

    debug_str = " | ".join(debug_messages)
    return {"windows": windows_info, "debug": debug_str}


def switch_to_app(app_name: str) -> str:
    """
    Switch to the specified application on macOS.
    """
    if sys.platform != "darwin":
        return "Window switching only supported on macOS"

    try:
        # Use PyObjC to activate the app
        workspace = NSWorkspace.sharedWorkspace()
        running_apps = workspace.runningApplications()

        for app in running_apps:
            if app.localizedName() == app_name:
                # Try to activate the app
                activated = app.activateWithOptions_(
                    1
                )  # NSApplicationActivateIgnoringOtherApps
                if activated:
                    return f"Switched to {app_name}"
                else:
                    return f"Failed to activate {app_name}"

        return f"Application '{app_name}' not found or not running"
    except Exception as e:
        return f"Error switching to app: {e}"
