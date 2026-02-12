"""
UI components for displaying docked apps and folders with clickable icons.
"""

import sys
import base64
import streamlit as st
from st_click_detector import click_detector


def render_dock_viewer(apps_handler, installed_apps=None):
    """
    Render the dock viewer section, showing docked apps and folders.
    Only displays on macOS.

    Args:
        apps_handler: The apps handler instance
        installed_apps: Optional dict of installed apps to reuse their icons
    """
    if sys.platform != "darwin":
        return

    docked_items = apps_handler.get_docked_apps(installed_apps)

    if not docked_items:
        return

    # Filter out debug items
    real_items = {k: v for k, v in docked_items.items() if v.get("type") != "debug"}

    if not real_items:
        return

    # Show all items
    items_list = list(real_items.items())

    st.subheader("Dock")

    # Build HTML content with clickable images
    items_html = []
    for idx, (name, item_data) in enumerate(items_list):
        icon_bytes = item_data.get("icon_bytes")

        if icon_bytes:
            # Check if it's SVG or PNG
            if icon_bytes.startswith(b"<?xml") or icon_bytes.startswith(b"<svg"):
                img_src = f"data:image/svg+xml;base64,{base64.b64encode(icon_bytes).decode('utf-8')}"
            else:
                img_src = f"data:image/png;base64,{base64.b64encode(icon_bytes).decode('utf-8')}"
        else:
            # Use a placeholder
            img_src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

        items_html.append(f'''
            <a href="#" id="{idx}" style="text-decoration: none; display: flex; flex-direction: column; align-items: center; padding: 5px;">
                <img src="{img_src}" style="width: 60px; height: 60px; border-radius: 10px;" />
                <span style="font-size: 12px; margin-top: 5px; font-family: monospace;">{name}</span>
            </a>
        ''')

    items_html_str = "".join(items_html)
    clickable_html = f'<div style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">{items_html_str}</div>'

    # Use click_detector to render and detect clicks
    clicked = click_detector(clickable_html)

    if clicked and clicked.strip():
        try:
            clicked_idx = int(clicked)
            if 0 <= clicked_idx < len(items_list):
                name, item_data = items_list[clicked_idx]
                command = item_data.get("command")
                msg = apps_handler.launch_app(command)
                st.toast(msg)
        except ValueError:
            pass
