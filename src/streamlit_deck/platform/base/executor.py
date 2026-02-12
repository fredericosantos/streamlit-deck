"""
Abstract base interface for OS-specific executor extensions.
"""

from abc import ABC


class BaseExecutorExt(ABC):
    """
    Interface for OS-specific executor extensions and overrides.
    """

    def extend_execute_hotkey(self, hotkey_string: str) -> str:
        """Optional extension for hotkey execution. Default no-op."""
        return ""

    def extend_execute_mouse(self, action: str) -> str:
        """Optional extension for mouse execution. Default no-op."""
        return ""
