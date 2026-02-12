"""
Shared utilities for app data handling in Streamlit Deck.
"""

from typing import Dict


def build_apps_reverse_map(apps_dict: Dict[str, Dict]) -> Dict[str, str]:
    """
    Build reverse mapping from command to app name.

    Args:
        apps_dict: Dict of {app_name: {'command': str, ...}}

    Returns:
        Dict of {command: app_name}
    """
    reverse_map = {}
    for app_name, app_data in apps_dict.items():
        if isinstance(app_data, dict) and "command" in app_data:
            reverse_map[app_data["command"]] = app_name
    return reverse_map
