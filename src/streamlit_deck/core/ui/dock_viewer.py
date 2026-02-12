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
    Only displays on macOS. Fixed at the bottom of the page.

    Args:
        apps_handler: The apps handler instance
        installed_apps: Optional dict of installed apps to reuse their icons
    """
    if sys.platform != "darwin":
        return

    # Add CSS for fixed dock at bottom
    st.markdown(
        """
    <style>
    .dock-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: var(--background-color);
        padding: 10px;
        border-top: 1px solid var(--secondary-background-color);
        z-index: 1000;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown('<div class="dock-footer">', unsafe_allow_html=True)
        st.subheader("Dock")

    docked_items = apps_handler.get_docked_apps(installed_apps)

    if docked_items:
        # Filter out debug items
        real_items = {k: v for k, v in docked_items.items() if v.get("type") != "debug"}

        if not real_items:
            # Show debug info if only debug items
            debug_items = {
                k: v for k, v in docked_items.items() if v.get("type") == "debug"
            }
            for name, item_data in debug_items.items():
                st.code(
                    f"Debug: {name}\n{item_data.get('error', item_data.get('data', 'No data'))}",
                    language="text",
                )
            return

        # Show all items (flexbox will handle wrapping)
        items_list = list(real_items.items())

        # Build HTML content with clickable images
        html_parts = [
            '<div style="display: flex; gap: 10px; justify-content: flex-start; flex-wrap: wrap;">'
        ]

        for idx, (name, item_data) in enumerate(items_list):
            icon_bytes = item_data.get("icon_bytes")
            command = item_data.get("command")

            if icon_bytes:
                # Check if it's SVG or PNG
                if icon_bytes.startswith(b"<?xml") or icon_bytes.startswith(b"<svg"):
                    # It's SVG, use it directly
                    img_src = f"data:image/svg+xml;base64,{base64.b64encode(icon_bytes).decode('utf-8')}"
                else:
                    # Assume it's PNG
                    img_src = f"data:image/png;base64,{base64.b64encode(icon_bytes).decode('utf-8')}"
            else:
                # Use a placeholder - 1x1 transparent PNG
                img_src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

            # Create clickable image with app name as ID
            # We'll use the index as the ID and map it back to the command
            html_parts.append(f'''
                <a href="#" id="{idx}" style="text-decoration: none; display: flex; flex-direction: column; align-items: center; padding: 5px;">
                    <img src="{img_src}" style="width: 60px; height: 60px; border-radius: 10px;" />
                    <span style="font-size: 12px; margin-top: 5px; color: inherit;">{name}</span>
                </a>
            ''')

        html_parts.append("</div>")
        html_content = "".join(html_parts)

        # Use click_detector to detect which icon was clicked
        clicked = click_detector(html_content)

        if clicked and clicked.strip():
            # clicked is the ID (index) of the clicked item
            try:
                clicked_idx = int(clicked)
                if 0 <= clicked_idx < len(items_list):
                    name, item_data = items_list[clicked_idx]
                    command = item_data.get("command")
                    msg = apps_handler.launch_app(command)
                    st.toast(msg)
            except ValueError:
                # Ignore invalid click values
                pass
    else:
        st.info("No docked items found.")

    st.markdown("</div>", unsafe_allow_html=True)
