"""
macOS-specific app detection and launching for Streamlit Deck.
"""

import os
import subprocess
import hashlib
from PIL import Image
from io import BytesIO
from typing import Dict
import plistlib
import urllib.parse

# macOS specific imports
try:
    from AppKit import NSWorkspace, NSApplicationActivationPolicyRegular
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGWindowListOptionOnScreenOnly,
        kCGWindowListExcludeDesktopElements,
        kCGNullWindowID,
    )
except ImportError:
    # These might fail if not on macOS or missing pyobjc
    pass

from ..base.apps import BaseApps


# Default icon for when extraction fails
DEFAULT_ICON_BYTES = None


def _get_default_icon():
    global DEFAULT_ICON_BYTES
    if DEFAULT_ICON_BYTES is None:
        from PIL import Image, ImageDraw

        img = Image.new("RGBA", (64, 64), (100, 149, 237, 255))  # Cornflower blue
        draw = ImageDraw.Draw(img)
        draw.rectangle([16, 16, 48, 48], fill=(255, 255, 255, 255))  # White square
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        DEFAULT_ICON_BYTES = buffer.getvalue()
    return DEFAULT_ICON_BYTES


class MacOSApps(BaseApps):
    def extract_macos_icon(self, app_path: str, size: tuple = (64, 64)) -> bytes:
        """
        Extracts icon from a macOS .app bundle and returns it as bytes.
        Prefers icns library if available, falls back to PIL
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
                return _get_default_icon()

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
            return _get_default_icon()

    def get_cached_icon(self, app_path: str) -> bytes:
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
        icon_bytes = self.extract_macos_icon(app_path)
        if icon_bytes:
            # Determine if it's SVG (starts with <?xml or <svg) or PNG
            if icon_bytes.startswith(b"<?xml") or icon_bytes.startswith(b"<svg"):
                cache_file = svg_cache_file
            else:
                cache_file = png_cache_file

            with open(cache_file, "wb") as f:
                f.write(icon_bytes)

        return icon_bytes

    def get_installed_apps(self) -> Dict[str, Dict[str, str]]:
        """
        Returns a dictionary of {App Name: {'command': str, 'icon_bytes': bytes}}
        Detected from .app bundles on macOS.
        """
        apps = {}

        paths = ["/Applications", os.path.expanduser("~/Applications")]

        for path in paths:
            if not os.path.exists(path):
                continue

            for item in os.listdir(path):
                if item.endswith(".app"):
                    name = item[:-4]  # Remove .app
                    full_path = os.path.join(path, item)

                    # Extract icon
                    icon_bytes = self.get_cached_icon(full_path)

                    apps[name] = {"command": full_path, "icon_bytes": icon_bytes}

        return dict(sorted(apps.items()))

    def launch_app(self, command: str) -> str:
        """
        Launches the application on macOS.
        """
        try:
            subprocess.Popen(["open", command])
            return f"Opened app: {os.path.basename(command)}"
        except Exception as e:
            return f"Error launching app: {e}"

    def get_apps_with_windows(self) -> dict:
        """
        Get applications with open windows on macOS.
        """
        debug_messages = []
        try:
            workspace = NSWorkspace.sharedWorkspace()
            running_apps = workspace.runningApplications()
            regular_apps = {}

            for app in running_apps:
                if app.activationPolicy() == NSApplicationActivationPolicyRegular:
                    app_name = app.localizedName()
                    bundle_id = app.bundleIdentifier()
                    pid = app.processIdentifier()

                    if app_name:
                        regular_apps[pid] = {
                            "name": app_name,
                            "bundle_id": bundle_id,
                            "pid": pid,
                            "is_active": app.isActive(),
                        }

            options = (
                kCGWindowListOptionOnScreenOnly | kCGWindowListExcludeDesktopElements
            )
            window_list = CGWindowListCopyWindowInfo(options, kCGNullWindowID)

            apps_with_windows = {}

            for window in window_list:
                owner_pid = window.get("kCGWindowOwnerPID")
                window_layer = window.get("kCGWindowLayer", 0)
                window_name = window.get("kCGWindowName", "")
                window_bounds = window.get("kCGWindowBounds", {})

                if window_layer != 0:
                    continue

                width = window_bounds.get("Width", 0)
                height = window_bounds.get("Height", 0)

                if width < 50 or height < 50:
                    continue

                if owner_pid in regular_apps:
                    app_info = regular_apps[owner_pid]

                    if owner_pid not in apps_with_windows:
                        apps_with_windows[owner_pid] = {
                            "name": app_info["name"],
                            "bundle_id": app_info["bundle_id"],
                            "pid": owner_pid,
                            "is_active": app_info["is_active"],
                            "windows": [],
                        }

                    apps_with_windows[owner_pid]["windows"].append(
                        {
                            "title": window_name if window_name else "<untitled>",
                            "width": width,
                            "height": height,
                            "x": window_bounds.get("X", 0),
                            "y": window_bounds.get("Y", 0),
                        }
                    )

            sorted_apps = sorted(
                apps_with_windows.values(),
                key=lambda x: (not x["is_active"], x["name"].lower()),
            )

            return {"apps": sorted_apps, "debug": " | ".join(debug_messages)}

        except Exception as e:
            return {"apps": [], "debug": f"Error: {e}"}

    def switch_to_app(self, app_name: str) -> str:
        """
        Switch to the specified application on macOS.
        """
        try:
            workspace = NSWorkspace.sharedWorkspace()
            running_apps = workspace.runningApplications()

            for app in running_apps:
                if app.localizedName() == app_name:
                    activated = app.activateWithOptions_(1)
                    if activated:
                        return f"Switched to {app_name}"
                    else:
                        return f"Failed to activate {app_name}"

            return f"Application '{app_name}' not found"
        except Exception as e:
            return f"Error switching to app: {e}"

    def get_docked_apps(self) -> Dict[str, Dict[str, any]]:
        """
        Get docked apps and folders from macOS Dock.
        Returns dict of {name: {'command': str, 'icon_bytes': bytes, 'type': str}}
        """
        plist_path = os.path.expanduser("~/Library/Preferences/com.apple.dock.plist")
        docked = {}

        try:
            with open(plist_path, "rb") as f:
                plist_data = plistlib.load(f)
        except Exception as e:
            docked["_debug_error"] = {
                "command": "",
                "icon_bytes": None,
                "type": "debug",
                "error": f"Failed to load plist: {e}",
            }
            return docked

        # Parse persistent-apps
        for item in plist_data.get("persistent-apps", []):
            tile_data = item.get("tile-data", {})
            file_data = tile_data.get("file-data", {})
            url = file_data.get("_CFURLString", "")
            if url.startswith("file://"):
                path = urllib.parse.unquote(url[7:])  # remove file:// and unquote
                label = tile_data.get(
                    "file-label", os.path.basename(path).replace(".app", "")
                )
                icon_bytes = (
                    self.get_cached_icon(path) if path.endswith(".app") else None
                )
                docked[label] = {
                    "command": path,
                    "icon_bytes": icon_bytes,
                    "type": "app",
                }

        # Parse persistent-others (folders, etc.)
        for item in plist_data.get("persistent-others", []):
            tile_data = item.get("tile-data", {})
            file_data = tile_data.get("file-data", {})
            url = file_data.get("_CFURLString", "")
            if url.startswith("file://"):
                path = urllib.parse.unquote(url[7:])
                label = tile_data.get("file-label", os.path.basename(path))
                # For folders, no icon for now
                docked[label] = {
                    "command": path,
                    "icon_bytes": _get_default_icon(),
                    "type": "folder",
                }

        # Debug if empty
        if not docked:
            docked["_debug_empty"] = {
                "command": "",
                "icon_bytes": None,
                "type": "debug",
                "data": f"Plist loaded, but no items. persistent-apps: {len(plist_data.get('persistent-apps', []))}, persistent-others: {len(plist_data.get('persistent-others', []))}",
            }

        return dict(sorted(docked.items()))
