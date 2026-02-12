"""
Shared utilities for hotkey handling in Streamlit Deck.
"""

from typing import List, Dict


def build_hotkey_string(
    draft_basic: List[str],
    draft_extended: List[str],
    basic_chars_map: Dict[str, str],
    extended_char_map: Dict[str, str],
) -> str:
    """
    Build a hotkey string from draft selections.

    Args:
        draft_basic: List of selected basic characters.
        draft_extended: List of selected extended characters.
        basic_chars_map: Mapping from display to internal basic chars.
        extended_char_map: Mapping from display to internal extended chars.

    Returns:
        Formatted hotkey string like "ctrl+shift+a".
    """
    keys = []
    modifiers = ["ctrl", "shift", "alt", "cmd"]

    # Add modifiers first
    sel_mods = [
        extended_char_map.get(k, k)
        for k in draft_extended
        if extended_char_map.get(k, k) in modifiers
    ]
    sel_other_ext = [
        extended_char_map.get(k, k)
        for k in draft_extended
        if extended_char_map.get(k, k) not in modifiers
    ]

    keys.extend(sel_mods)
    # Convert display basic chars back to internal (lowercase)
    keys.extend([basic_chars_map[c] for c in draft_basic])
    keys.extend(sel_other_ext)

    return "+".join(keys) if keys else ""
