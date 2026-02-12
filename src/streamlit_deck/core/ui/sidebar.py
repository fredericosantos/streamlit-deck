import streamlit as st
from streamlit_deck.backend.config import (
    list_layouts,
    save_layout,
    create_default_layout,
)


def render_sidebar(layout):
    st.sidebar.title("Streamlit Deck")

    # Layout Selection
    layout_list = list_layouts()
    if not layout_list:
        layout_list = ["default"]

    selected_layout = st.sidebar.selectbox(
        "Profile",
        layout_list,
        index=layout_list.index(st.session_state.current_layout_name)
        if st.session_state.current_layout_name in layout_list
        else 0,
    )

    if selected_layout != st.session_state.current_layout_name:
        st.session_state.current_layout_name = selected_layout
        st.session_state.selected_button = None
        st.rerun()

    # New Layout
    with st.sidebar.expander("Manage Profiles"):
        new_layout_name = st.text_input("New Profile Name")
        if st.button("Create Profile"):
            if new_layout_name:
                save_layout(new_layout_name, create_default_layout(new_layout_name))
                st.session_state.current_layout_name = new_layout_name
                st.rerun()

    # Mode Toggle
    st.sidebar.divider()
    st.session_state.edit_mode = st.sidebar.toggle(
        "Edit Mode", value=st.session_state.edit_mode
    )

    # --- Grid Settings (Only in Edit Mode) ---
    if st.session_state.edit_mode:
        with st.sidebar.expander("Grid Settings", expanded=True):
            rows = layout.get("rows", 2)
            cols = layout.get("cols", 2)

            c1, c2 = st.columns(2)
            with c1:
                st.caption("Rows")
                if st.button("➖", key="dec_row"):
                    layout["rows"] = max(1, rows - 1)
                    save_layout(st.session_state.current_layout_name, layout)
                    st.rerun()
                st.markdown(
                    f"<div style='text-align: center; font-size: 20px; font-weight: bold;'>{rows}</div>",
                    unsafe_allow_html=True,
                )
                if st.button("➕", key="inc_row"):
                    layout["rows"] = min(8, rows + 1)
                    save_layout(st.session_state.current_layout_name, layout)
                    st.rerun()

            with c2:
                st.caption("Columns")
                if st.button("➖", key="dec_col"):
                    layout["cols"] = max(1, cols - 1)
                    save_layout(st.session_state.current_layout_name, layout)
                    st.rerun()
                st.markdown(
                    f"<div style='text-align: center; font-size: 20px; font-weight: bold;'>{cols}</div>",
                    unsafe_allow_html=True,
                )
                if st.button("➕", key="inc_col"):
                    layout["cols"] = min(8, cols + 1)
                    save_layout(st.session_state.current_layout_name, layout)
                    st.rerun()
