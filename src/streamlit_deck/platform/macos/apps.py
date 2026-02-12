"""
macOS-specific app detection and launching for Streamlit Deck.
"""

import os
import subprocess
import hashlib
from PIL import Image
from io import BytesIO
from typing import Dict
from .base.apps import BaseApps


class MacOSApps(BaseApps):
    def extract_macos_icon(self, app_path: str, size: tuple = (64, 64)) -> bytes:
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
