"""
Abstract base interface for OS-specific app detection and launching.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseApps(ABC):
    """
    Interface for OS-specific application handling.
    """

    @abstractmethod
    def get_installed_apps(self) -> Dict[str, Dict[str, str]]:
        """Return dict of {app_name: {'command': str, 'icon_bytes': bytes}}."""
        pass

    @abstractmethod
    def launch_app(self, command: str) -> str:
        """Launch an application by command, return status message."""
        pass

    def get_apps_with_windows(self) -> dict:
        """Get list of apps with open windows. Default empty for non-macOS."""
        return {"apps": [], "debug": "Not supported on this OS"}

    def switch_to_app(self, app_name: str) -> str:
        """Switch to an app by name. Default no-op for non-macOS."""
        return f"Switch to app not supported on {__import__('sys').platform}"

    def get_docked_apps(self) -> Dict[str, Dict[str, Any]]:
        """Get docked apps/folders. Default empty for non-macOS."""
        return {}
