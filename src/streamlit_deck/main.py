import streamlit as st
import os
from streamlit_deck.backend import config, executor

# Page Config
st.set_page_config(
    page_title="Streamlit Deck", layout="wide", initial_sidebar_state="expanded"
)

# Custom CSS for better button styling
st.markdown(
    """
<style>
    .stButton button {
        height: 100px;
        width: 100%;
        font-size: 24px;
        font-weight: bold;
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

# --- Sidebar ---
st.sidebar.title("Streamlit Deck")

# Layout Selection
layout_list = config.list_layouts()
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
            config.save_layout(
                new_layout_name, config.create_default_layout(new_layout_name)
            )
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
                config.save_layout(st.session_state.current_layout_name, layout)
                st.rerun()
            st.markdown(
                f"<div style='text-align: center; font-size: 20px; font-weight: bold;'>{rows}</div>",
                unsafe_allow_html=True,
            )
            if st.button("➕", key="inc_row"):
                layout["rows"] = min(8, rows + 1)
                config.save_layout(st.session_state.current_layout_name, layout)
                st.rerun()

        with c2:
            st.caption("Columns")
            if st.button("➖", key="dec_col"):
                layout["cols"] = max(1, cols - 1)
                config.save_layout(st.session_state.current_layout_name, layout)
                st.rerun()
            st.markdown(
                f"<div style='text-align: center; font-size: 20px; font-weight: bold;'>{cols}</div>",
                unsafe_allow_html=True,
            )
            if st.button("➕", key="inc_col"):
                layout["cols"] = min(8, cols + 1)
                config.save_layout(st.session_state.current_layout_name, layout)
                st.rerun()

# --- Editor Panel (Sidebar) ---
if st.session_state.edit_mode and st.session_state.selected_button:
    st.sidebar.header("Edit Button")
    r, c = st.session_state.selected_button
    btn_id = f"{r}-{c}"
    btn_data = layout["buttons"].get(btn_id, {})

    with st.sidebar.form("edit_button"):
        st.write(f"Editing Button at Row {r + 1}, Col {c + 1}")

        new_label = st.text_input("Label", value=btn_data.get("label", ""))

        action_type = st.selectbox(
            "Action Type",
            ["hotkey", "script"],
            index=0 if btn_data.get("type") == "hotkey" else 1,
        )

        payload = ""
        if action_type == "hotkey":
            payload = st.text_input(
                "Hotkey (e.g. ctrl+c, volumedown)", value=btn_data.get("action", "")
            )
            st.caption(
                "Common keys: ctrl, shift, alt, command, f1-f12, enter, space, playpause, volumemute"
            )
        else:
            scripts = config.list_scripts()
            current_script = btn_data.get("action", "")
            idx = scripts.index(current_script) if current_script in scripts else 0
            if scripts:
                payload = st.selectbox("Select Script", scripts, index=idx)
            else:
                st.warning("No scripts found in scripts/ directory")
                payload = ""

        # Color (Hex) - Optional
        # color = st.color_picker("Color", value=btn_data.get("color", "#F0F2F6"))

        if st.form_submit_button("Save"):
            # Update layout data
            if btn_id not in layout["buttons"]:
                layout["buttons"][btn_id] = {}

            layout["buttons"][btn_id] = {
                "row": r,
                "col": c,
                "label": new_label,
                "type": action_type,
                "action": payload,
            }
            config.save_layout(st.session_state.current_layout_name, layout)
            st.toast("Button Saved!")
            st.rerun()

    if st.sidebar.button("Clear Button", type="primary"):
        if btn_id in layout["buttons"]:
            del layout["buttons"][btn_id]
            config.save_layout(st.session_state.current_layout_name, layout)
            st.rerun()

# --- Main Grid ---
rows = layout.get("rows", 2)
cols = layout.get("cols", 2)

# Grid Layout
with st.container(border=True):
    for r in range(rows):
        columns = st.columns(cols)
        for c in range(cols):
            btn_id = f"{r}-{c}"
            btn_data = layout["buttons"].get(btn_id, {})

            # Default state:
            # Edit Mode: Show "➕" if empty
            # Run Mode: Show nothing (empty space) if empty

            label = btn_data.get("label", "")
            if not label and st.session_state.edit_mode:
                label = "➕"

            with columns[c]:
                if label:
                    # Unique key is crucial
                    clicked = st.button(
                        label, key=f"btn_{r}_{c}", use_container_width=True
                    )

                    if clicked:
                        if st.session_state.edit_mode:
                            st.session_state.selected_button = (r, c)
                            st.rerun()
                        else:
                            # Execute Action
                            if btn_data:
                                msg = executor.execute_action(
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

# --- Footer / Info ---
if st.session_state.edit_mode:
    st.info(f"Layout: {layout.get('name')} | Size: {rows}x{cols}")
