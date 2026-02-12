"""
Linux-specific character mappings for Streamlit Deck.
"""

from typing import Dict, List
from ..base.mappings import BaseMappings


class LinuxMappings(BaseMappings):
    """
    Linux-specific key mappings and character sets.
    """

    @property
    def extended_chars(self) -> List[str]:
        return [
            "Ctrl",
            "Shift",
            "Alt",
            "Super",
            "Enter",
            "Esc",
            "Tab",
            "Space",
            "Backspace",
            "Delete",
            "Up",
            "Down",
            "Left",
            "Right",
            "CapsLock",
        ] + [f"F{i}" for i in range(1, 13)]

    @property
    def extended_char_map(self) -> Dict[str, str]:
        mapping = super().extended_char_map
        mapping.update(
            {
                "Ctrl": "ctrl",
                "Shift": "shift",
                "Alt": "alt",
                "Super": "cmd",  # Maps to cmd in backend KEY_MAP
                "Enter": "enter",
                "Esc": "esc",
                "Tab": "tab",
                "Space": "space",
                "Backspace": "backspace",
                "Delete": "delete",
                "Up": "up",
                "Down": "down",
                "Left": "left",
                "Right": "right",
                "CapsLock": "capslock",
            }
        )
        return mapping
