"""
Grid rendering and interaction for Streamlit Deck.
"""

import streamlit as st
from streamlit_deck.shared.app_utils import build_apps_reverse_map
from streamlit_deck.core.ui.components import render_icon_button


def render_grid(layout, edit_mode, selected_button, current_layout_name, APPS_DICT):
    rows = layout.get("rows", 2)
    cols = layout.get("cols", 2)

    apps_reverse_map = build_apps_reverse_map(APPS_DICT)

    # Grid Layout
    with st.container(border=False):
        for r in range(rows):
            columns = st.columns(cols)
            for c in range(cols):
                btn_id = f"{r}-{c}"
                btn_data = layout["buttons"].get(btn_id, {})

                # Default state:
                # Edit Mode: Show "➕" if empty
                # Run Mode: Show nothing (empty space) if empty

                label = btn_data.get("label", "")
                btn_type = btn_data.get("type", "")
                action = btn_data.get("action", "")

                if not label and edit_mode:
                    label = "➕"

                # Append shortcut to label for hotkey actions
                if btn_type == "hotkey" and action and label != "➕":
                    label = f"{label} ({action})"

                with columns[c]:
                    if label:
                        # Determine button type (primary if selected in edit mode)
                        btn_display_type = "secondary"
                        if edit_mode and selected_button == (r, c):
                            btn_display_type = "primary"

                        # Prepare icon for app buttons
                        icon_bytes = None
                        if btn_type == "app" and action:
                            app_name = apps_reverse_map.get(action)
                            if app_name and APPS_DICT[app_name].get("icon_bytes"):
                                icon_bytes = APPS_DICT[app_name]["icon_bytes"]

                        # Unique key is crucial
                        # Add shortcut for quick access (numbers for first 9 buttons)
                        shortcut = None
                        if not edit_mode and rows <= 3 and cols <= 3:
                            # Map position to number (1-9) for small grids
                            shortcut_num = r * cols + c + 1
                            if shortcut_num <= 9:
                                shortcut = str(shortcut_num)

                        clicked = render_icon_button(
                            icon_bytes=icon_bytes,
                            label=label,
                            key=f"btn_{r}_{c}",
                            type=btn_display_type,
                            shortcut=shortcut,
                        )

                        if clicked:
                            if edit_mode:
                                st.session_state.selected_button = (r, c)
                                st.rerun()
                            else:
                                # Execute Action
                                if btn_data:
                                    from streamlit_deck.core.backend.base_executor import (
                                        execute_action,
                                    )

                                    msg = execute_action(
                                        btn_data.get("type"), btn_data.get("action")
                                    )
                                    st.toast(msg)
                    else:
                        # Render empty placeholder to maintain grid alignment
                        st.markdown(
                            "<div style='height: 100px;'></div>", unsafe_allow_html=True
                        )
                        # If in edit mode, we want this to be clickable to add a button.
                        # But st.button with empty label is weird.
                        # The logic above sets label="➕" in edit mode, so we only fall here in Run Mode.

    # Global keyboard shortcut handler for grid buttons (numbers 1-9)
    if not edit_mode and rows <= 3 and cols <= 3:
        # Add keyboard event listener using Streamlit's session state
        st.markdown(
            f"""
            <script>
            document.addEventListener('keydown', function(event) {{
                // Only handle single digit keys without modifiers
                if (event.key >= '1' && event.key <= '9' && !event.ctrlKey && !event.altKey && !event.metaKey && !event.shiftKey) {{
                    const num = parseInt(event.key);
                    const maxButtons = {rows * cols};
                    if (num <= maxButtons) {{
                        // Calculate row and col from number (1-based to 0-based)
                        const col = {cols};
                        const r = Math.floor((num - 1) / col);
                        const c = (num - 1) % col;
                        const btnId = `btn_${{r}}_${{c}}`;
                        const button = document.querySelector(`button[key="${{btnId}}"]`);
                        if (button) {{
                            event.preventDefault();
                            button.click();
                        }}
                    }}
                }}
            }});
            </script>
            """,
            unsafe_allow_html=True,
        )
