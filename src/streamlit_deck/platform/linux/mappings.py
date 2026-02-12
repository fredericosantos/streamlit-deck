"""
Linux-specific character mappings for Streamlit Deck.
"""

import string
from typing import Dict, List


class LinuxMappings:
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
        mapping = {
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
        # Add function keys
        for i in range(1, 13):
            mapping[f"F{i}"] = f"f{i}"
        return mapping

    @property
    def basic_chars_display(self) -> List[str]:
        return (
            [c.upper() for c in string.ascii_lowercase]
            + list(string.digits)
            + list("!@#$%^&*()[]{}|;:,.<>?/")
        )

    @property
    def basic_chars_map(self) -> Dict[str, str]:
        mapping = {c.upper(): c for c in string.ascii_lowercase}
        mapping.update({d: d for d in string.digits})  # Digits map to themselves
        mapping.update(
            {p: p for p in "!@#$%^&*()[]{}|;:,.<>?/"}
        )  # Punctuation maps to itself
        return mapping
