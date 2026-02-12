import streamlit as st
from .core.backend import config
import sys

from .shared.ui_utils import display_icon_in_column
from .platform import get_apps
from .core.ui.sidebar import render_sidebar
from .core.ui.grid import render_grid

st.set_page_config(
    page_title="Streamlit Deck",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon=":material/deck:",  # Material Design icon for deck
)

# Custom CSS for better button styling
st.markdown(
    """
<style>
    .stButton button {
        height: 60px !important;  /* Reduced from 100px to 60px */
        font-size: 18px !important;  /* Slightly smaller font */
        font-weight: bold;
    }
    /* Center icons vertically in their containers */
    .icon-container {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 60px !important;  /* Match button height */
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- State Management ---
if "current_layout_name" not in st.session_state:
    st.session_state.current_layout_name = "default"
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "selected_button" not in st.session_state:
    st.session_state.selected_button = None  # (row, col)

# Load Layout
layout = config.load_layout(st.session_state.current_layout_name)

# Load apps data for icon access
apps_handler = get_apps()
APPS_DICT = apps_handler.get_installed_apps()

render_sidebar(layout)

render_grid(
    layout,
    st.session_state.edit_mode,
    st.session_state.selected_button,
    st.session_state.current_layout_name,
    APPS_DICT,
)

# --- Open Windows Container ---
st.subheader("Open Windows")
apps_data = apps_handler.get_apps_with_windows()
apps_list = apps_data["apps"]
debug = apps_data["debug"]

# Flatten windows from all apps
windows = []
for app in apps_list:
    for window in app["windows"]:
        windows.append(
            {
                "title": window["title"],
                "app_name": app["name"],
                "is_active": app["is_active"],
                "bundle_id": app["bundle_id"],
            }
        )

if windows:
    # Display windows in a 4-column grid
    num_cols = 4
    window_rows = (len(windows) + num_cols - 1) // num_cols  # Ceiling division

    for window_row in range(window_rows):
        window_cols = st.columns(num_cols)
        for col_idx in range(num_cols):
            window_idx = window_row * num_cols + col_idx
            if window_idx < len(windows):
                window_info = windows[window_idx]

                with window_cols[col_idx]:
                    window_title = window_info["title"]
                    app_name = window_info["app_name"]
                    is_active = window_info["is_active"]

                    # Add active indicator
                    button_label = f"{window_title} {'●' if is_active else ''}"

                    # Truncate long titles
                    if len(button_label) > 15:
                        button_label = button_label[:12] + "..."

                    if st.button(
                        button_label,
                        key=f"window_{window_idx}",
                        use_container_width=True,
                        help=f"App: {app_name} | Bundle: {window_info['bundle_id']}",
                    ):
                        msg = apps_handler.switch_to_app(app_name)
                        st.toast(msg)
else:
    st.info("No open windows detected. This feature is macOS-only.")
    if debug:
        st.code(f"Debug: {debug}", language="text")

st.divider()

if st.session_state.edit_mode and st.session_state.selected_button:
    r, c = st.session_state.selected_button
    btn_id = f"{r}-{c}"
    btn_data = layout["buttons"].get(btn_id, {})

    from .core.ui.editor import render_editor

    render_editor(layout, r, c, btn_id, btn_data, APPS_DICT)

# --- Footer / Info ---
if st.session_state.edit_mode:
    layout_name = layout.get("name", "Default")  # Add default value
    rows = layout.get("rows", 2)
    cols = layout.get("cols", 2)
    st.info(f"Layout: {layout_name} | Size: {rows}x{cols}")
