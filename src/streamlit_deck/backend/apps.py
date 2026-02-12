import os
import sys
import glob
import subprocess
import hashlib
import shlex
from PIL import Image
from io import BytesIO
from typing import Dict, Optional

# macOS specific imports
if sys.platform == "darwin":
    from AppKit import NSWorkspace, NSApplicationActivationPolicyRegular
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGWindowListOptionOnScreenOnly,
        kCGWindowListExcludeDesktopElements,
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
            cmd_list = shlex.split(command)
            subprocess.Popen(cmd_list, start_new_session=True)
            return f"Launched command: {command}"
    except Exception as e:
        return f"Error launching app: {e}"


def get_apps_with_windows() -> dict:
    """
    Get applications with open windows, similar to Cmd+Tab app switcher.
    Filters out system utilities, notification center, and background processes.
    Returns dict with 'apps' list and 'debug' string
    """
    debug_messages = []

    if sys.platform != "darwin":
        return {"apps": [], "debug": "Not macOS"}

    try:
        workspace = NSWorkspace.sharedWorkspace()

        # Get all running applications with regular activation policy
        # This filters out background processes and system utilities
        running_apps = workspace.runningApplications()
        regular_apps = {}

        for app in running_apps:
            # Only include apps that appear in Dock (regular activation policy)
            if app.activationPolicy() == NSApplicationActivationPolicyRegular:
                app_name = app.localizedName()
                bundle_id = app.bundleIdentifier()
                pid = app.processIdentifier()

                if app_name:  # Only if has name
                    regular_apps[pid] = {
                        "name": app_name,
                        "bundle_id": bundle_id,
                        "pid": pid,
                        "is_active": app.isActive(),
                    }
                    debug_messages.append(
                        f"Regular app: {app_name} (PID: {pid}, Active: {app.isActive()})"
                    )

        debug_messages.append(f"Found {len(regular_apps)} regular apps")

        # Get window list - exclude desktop elements and only get on-screen windows
        options = kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements
        window_list = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
        debug_messages.append(f"Found {len(window_list)} windows from Quartz")

        # Track which apps have actual windows
        apps_with_windows = {}

        for window in window_list:
            owner_pid = window.get("kCGWindowOwnerPID")
            window_layer = window.get("kCGWindowLayer", 0)
            window_name = window.get("kCGWindowName", "")
            window_bounds = window.get("kCGWindowBounds", {})

            # Only consider windows in layer 0 (normal application windows)
            # Skip windows without meaningful dimensions
            if window_layer != 0:
                continue

            width = window_bounds.get("Width", 0)
            height = window_bounds.get("Height", 0)

            # Filter out tiny windows (often helper windows or popups)
            if width < 50 or height < 50:
                debug_messages.append(
                    f"Skipped tiny window: {window_name} ({width}x{height})"
                )
                continue

            # Check if this window belongs to a regular app
            if owner_pid in regular_apps:
                app_info = regular_apps[owner_pid]
                debug_messages.append(
                    f"Window: {window_name} ({width}x{height}) from {app_info['name']}"
                )

                # Add app to results if not already there
                if owner_pid not in apps_with_windows:
                    apps_with_windows[owner_pid] = {
                        "name": app_info["name"],
                        "bundle_id": app_info["bundle_id"],
                        "pid": owner_pid,
                        "is_active": app_info["is_active"],
                        "windows": [],
                    }

                # Add window info
                apps_with_windows[owner_pid]["windows"].append(
                    {
                        "title": window_name if window_name else "<untitled>",
                        "width": width,
                        "height": height,
                        "x": window_bounds.get("X", 0),
                        "y": window_bounds.get("Y", 0),
                    }
                )

        # Sort by active status (active apps first), then by name
        sorted_apps = sorted(
            apps_with_windows.values(),
            key=lambda x: (not x["is_active"], x["name"].lower()),
        )

        debug_messages.append(f"Final result: {len(sorted_apps)} apps with windows")

        debug_str = " | ".join(debug_messages)
        return {"apps": sorted_apps, "debug": debug_str}

    except Exception as e:
        debug_messages.append(f"Error: {e}")
        debug_str = " | ".join(debug_messages)
        return {"apps": [], "debug": debug_str}


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
