"""
UI components for displaying docked apps and folders.
"""

import sys
import streamlit as st
from ...core.ui.components import render_icon_button


def render_dock_viewer(apps_handler):
    """
    Render the dock viewer section, showing docked apps and folders.
    Only displays on macOS.
    """
    if sys.platform != "darwin":
        return

    st.subheader("Dock")

    docked_items = apps_handler.get_docked_apps()

    if docked_items:
        # Display items in a 4-column grid
        num_cols = 4
        items_list = list(docked_items.items())
        item_rows = (len(items_list) + num_cols - 1) // num_cols  # Ceiling division

        for item_row in range(item_rows):
            item_cols = st.columns(num_cols)
            for col_idx in range(num_cols):
                item_idx = item_row * num_cols + col_idx
                if item_idx < len(items_list):
                    name, item_data = items_list[item_idx]

                    with item_cols[col_idx]:
                        if item_data.get("type") == "debug":
                            # Display debug info
                            st.code(
                                f"Debug: {name}\n{item_data.get('error', item_data.get('data', 'No data'))}",
                                language="text",
                            )
                        else:
                            icon_bytes = item_data.get("icon_bytes")
                            command = item_data.get("command")

                            # Use render_icon_button for consistent styling
                            if render_icon_button(
                                icon_bytes,
                                name,
                                f"dock_{item_idx}",
                                use_container_width=True,
                            ):
                                # Launch the item on click
                                msg = apps_handler.launch_app(command)
                                st.toast(msg)
    else:
        st.info("No docked items found.")
