import streamlit as st
import os
from src.backend import config, executor

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
rows = layout.get("rows", 4)
cols = layout.get("cols", 3)

# Grid Layout
for r in range(rows):
    columns = st.columns(cols)
    for c in range(cols):
        btn_id = f"{r}-{c}"
        btn_data = layout["buttons"].get(btn_id, {})
        label = btn_data.get("label", "➕" if st.session_state.edit_mode else "")

        # If empty in run mode, show nothing or placeholder?
        # Better to show empty button so layout is preserved.

        with columns[c]:
            # Unique key is crucial
            clicked = st.button(label, key=f"btn_{r}_{c}", use_container_width=True)

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
                        pass  # Empty button

# --- Footer / Info ---
if st.session_state.edit_mode:
    st.info(f"Layout: {layout.get('name')} | Size: {rows}x{cols}")
