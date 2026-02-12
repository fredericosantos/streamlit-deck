"""
macOS-specific character mappings for Streamlit Deck.
"""

from typing import Dict, List
from ..base.mappings import BaseMappings


class MacOSMappings(BaseMappings):
    """
    macOS-specific key mappings and character sets.
    """

    @property
    def extended_chars(self) -> List[str]:
        return [
            "⌃ ctrl",
            "⇧ shift",
            "⌥ alt",
            "⌘ cmd",
            "↵ enter",
            "⎋ esc",
            "⇥ tab",
            "␣ space",
            "⌫ backspace",
            "⌦ delete",
            "↑ up",
            "↓ down",
            "← left",
            "→ right",
            "⇪ capslock",
        ] + [f"F{i}" for i in range(1, 13)]

    @property
    def extended_char_map(self) -> Dict[str, str]:
        mapping = super().extended_char_map
        mapping.update(
            {
                "⌃ ctrl": "ctrl",
                "⇧ shift": "shift",
                "⌥ alt": "alt",
                "⌘ cmd": "cmd",
                "↵ enter": "enter",
                "⎋ esc": "esc",
                "⇥ tab": "tab",
                "␣ space": "space",
                "⌫ backspace": "backspace",
                "⌦ delete": "delete",
                "↑ up": "up",
                "↓ down": "down",
                "← left": "left",
                "→ right": "right",
                "⇪ capslock": "capslock",
            }
        )
        return mapping
