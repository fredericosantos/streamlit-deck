"""
macOS-specific character mappings for Streamlit Deck.
"""

import string
from typing import Dict, List


class MacOSMappings:
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
        mapping = {
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
