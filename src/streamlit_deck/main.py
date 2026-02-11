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
# Moved to below grid in Edit Mode

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
                    # Determine button type (primary if selected in edit mode)
                    btn_type = "secondary"
                    if (
                        st.session_state.edit_mode
                        and st.session_state.selected_button == (r, c)
                    ):
                        btn_type = "primary"

                    # Unique key is crucial
                    clicked = st.button(
                        label,
                        key=f"btn_{r}_{c}",
                        use_container_width=True,
                        type=btn_type,
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

# --- Editor Interface (Below Grid) ---
if st.session_state.edit_mode and st.session_state.selected_button:
    import string

    r, c = st.session_state.selected_button
    btn_id = f"{r}-{c}"
    btn_data = layout["buttons"].get(btn_id, {})

    st.divider()
    st.subheader(f"Editing Button: Row {r + 1}, Col {c + 1}")

    # --- Pre-calculate Defaults ---
    # Define lists first so we can use them for matching
    basic_chars = list(string.ascii_lowercase + string.digits)
    extended_chars = [
        "ctrl",
        "shift",
        "alt",
        "cmd",
        "enter",
        "esc",
        "tab",
        "space",
        "backspace",
        "delete",
        "up",
        "down",
        "left",
        "right",
        "capslock",
    ] + [f"f{i}" for i in range(1, 13)]
    scripts_list = config.list_scripts()
    media_keys = [
        "playpause",
        "volumemute",
        "volumeup",
        "volumedown",
        "nexttrack",
        "prevtrack",
    ]
    mouse_actions = [
        "left_click",
        "right_click",
        "middle_click",
        "double_left_click",
    ]

    # Initialize defaults
    def_basic = []
    def_extended = []
    def_media = []
    def_script = None
    def_mouse = None

    current_type = btn_data.get("type", "hotkey")
    current_action = btn_data.get("action", "")

    if current_type == "script":
        if current_action in scripts_list:
            def_script = current_action
    elif current_type == "mouse":
        if current_action in mouse_actions:
            def_mouse = current_action
    elif current_type == "hotkey":
        keys = current_action.split("+")
        for k in keys:
            k = k.strip().lower()
            if k in basic_chars:
                def_basic.append(k)
            elif k in extended_chars:
                def_extended.append(k)
            elif k in media_keys:
                def_media.append(k)

    with st.container(border=True):
        with st.form("edit_button_form"):
            # Manual Overrides
            c1, c2 = st.columns(2)
            with c1:
                current_label = st.text_input(
                    "Button Label", value=btn_data.get("label", "")
                )
            with c2:
                current_action_input = st.text_input(
                    "Action Payload (Auto-filled by selections)",
                    value=btn_data.get("action", ""),
                    help="Manually edit this if needed. Selections below will overwrite this.",
                )

            # --- Selection Expanders ---

            # 1. Basic Characters
            with st.expander("Basic Characters"):
                selected_basic = st.pills(
                    "Select Characters",
                    basic_chars,
                    selection_mode="multi",
                    default=def_basic,
                )

            # 2. Extended Characters
            with st.expander("Extended Characters"):
                selected_extended = st.pills(
                    "Select Special Keys",
                    extended_chars,
                    selection_mode="multi",
                    default=def_extended,
                )

            # 3. Functions (Scripts)
            with st.expander("Functions (Scripts)"):
                if scripts_list:
                    selected_script = st.pills(
                        "Select Script",
                        scripts_list,
                        selection_mode="single",
                        default=def_script,
                    )
                else:
                    st.warning("No scripts found in scripts/ directory")
                    selected_script = None

            # 4. Media and Audio Control
            with st.expander("Media & Audio"):
                selected_media = st.pills(
                    "Media Controls",
                    media_keys,
                    selection_mode="multi",
                    default=def_media,
                )

            # 5. Mouse
            with st.expander("Mouse"):
                selected_mouse = st.pills(
                    "Mouse Actions",
                    mouse_actions,
                    selection_mode="single",
                    default=def_mouse,
                )

            # --- Save Logic ---
            st.write("")
            submitted = st.form_submit_button("Save", type="primary")

            if submitted:
                # Determine Action Type and Payload
                final_type = "hotkey"
                final_payload = current_action_input

                # Priority: Script > Mouse > Keys (Basic/Extended/Media)

                if selected_script:
                    final_type = "script"
                    final_payload = selected_script
                    if not current_label:
                        current_label = selected_script

                elif selected_mouse:
                    final_type = "mouse"
                    final_payload = selected_mouse
                    if not current_label:
                        current_label = selected_mouse.replace("_", " ").title()

                else:
                    # Check if any keys selected
                    all_keys = []
                    modifiers = ["ctrl", "shift", "alt", "cmd"]

                    selected_mods = [
                        k for k in (selected_extended or []) if k in modifiers
                    ]
                    other_extended = [
                        k for k in (selected_extended or []) if k not in modifiers
                    ]

                    all_keys.extend(selected_mods)
                    if selected_basic:
                        all_keys.extend(selected_basic)
                    all_keys.extend(other_extended)
                    if selected_media:
                        all_keys.extend(selected_media)

                    if all_keys:
                        final_type = "hotkey"
                        final_payload = "+".join(all_keys)
                        if not current_label:
                            current_label = final_payload
                    # If no keys selected, we fall back to final_payload = current_action_input (manual)

                # Save
                if btn_id not in layout["buttons"]:
                    layout["buttons"][btn_id] = {}

                layout["buttons"][btn_id] = {
                    "row": r,
                    "col": c,
                    "label": current_label,
                    "type": final_type,
                    "action": final_payload,
                }
                config.save_layout(st.session_state.current_layout_name, layout)
                st.toast("Button Saved!")
                st.rerun()

        # Clear Button (Outside Form)
        if st.button("Clear Button"):
            if btn_id in layout["buttons"]:
                del layout["buttons"][btn_id]
                config.save_layout(st.session_state.current_layout_name, layout)
                st.rerun()

# --- Footer / Info ---
if st.session_state.edit_mode:
    st.info(f"Layout: {layout.get('name')} | Size: {rows}x{cols}")
