"""
macOS-specific executor extensions for Streamlit Deck.
"""


class MacOSExecutorExt:
    """
    macOS-specific extensions to the base executor.
    """

    def extend_execute_hotkey(self, hotkey_string: str) -> str:
        """Optional extension for hotkey execution on macOS."""
        # For now, no extension - base handles it
        return ""

    def extend_execute_mouse(self, action: str) -> str:
        """Optional extension for mouse execution on macOS."""
        # For now, no extension - base handles it
        return ""
