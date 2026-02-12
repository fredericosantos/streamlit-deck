import streamlit as st
from streamlit_deck.core.backend import config

from streamlit_deck.platform import get_apps
from streamlit_deck.core.ui.sidebar import render_sidebar
from streamlit_deck.core.ui.grid import render_grid
from streamlit_deck.core.ui.windows import render_open_windows
from streamlit_deck.core.ui.dock_viewer import render_dock_viewer

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

st.divider()

if st.session_state.edit_mode and st.session_state.selected_button:
    r, c = st.session_state.selected_button
    btn_id = f"{r}-{c}"
    btn_data = layout["buttons"].get(btn_id, {})

    from streamlit_deck.core.ui.editor import render_editor

    render_editor(layout, r, c, btn_id, btn_data, APPS_DICT)

# --- Footer / Info ---
if st.session_state.edit_mode:
    layout_name = layout.get("name", "Default")  # Add default value
    rows = layout.get("rows", 2)
    cols = layout.get("cols", 2)
    st.info(f"Layout: {layout_name} | Size: {rows}x{cols}")

# --- Open Windows ---
render_open_windows(apps_handler)

# --- Dock Viewer ---
render_dock_viewer(apps_handler)
