import streamlit as st
import os
import tempfile
from streamlit_deck.backend import config, executor, apps

# Page Config
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

# Load apps data for icon access
APPS_DICT = apps.get_installed_apps()

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
            btn_type = btn_data.get("type", "")
            action = btn_data.get("action", "")

            if not label and st.session_state.edit_mode:
                label = "➕"

            with columns[c]:
                if label:
                    # Determine button type (primary if selected in edit mode)
                    btn_display_type = "secondary"
                    if (
                        st.session_state.edit_mode
                        and st.session_state.selected_button == (r, c)
                    ):
                        btn_display_type = "primary"

                    # Show app icon if this is an app button
                    if btn_type == "app" and action:
                        app_name = None
                        # Find app name from command using APPS_REVERSE
                        for name, data in APPS_DICT.items():
                            if isinstance(data, dict) and data.get("command") == action:
                                app_name = name
                                break

                        if app_name and APPS_DICT[app_name].get("icon_bytes"):
                            # Use image button component instead of separate icon + button
                            from st_image_button import st_image_button

                            # Save icon bytes to temporary PNG file
                            with tempfile.NamedTemporaryFile(
                                suffix=".png", delete=False
                            ) as tmp:
                                tmp.write(APPS_DICT[app_name]["icon_bytes"])
                                tmp.flush()

                                # Use image button component
                                clicked = st_image_button(
                                    text=label,  # Button text/label
                                    image=tmp.name,  # Path to temp image file
                                    width="48px",  # Size as requested
                                    variant="outlined"
                                    if btn_display_type == "secondary"
                                    else "filled",
                                    key=f"deck_img_btn_{r}_{c}",
                                )

                                # Clean up temp file
                                try:
                                    os.unlink(tmp.name)
                                except:
                                    pass  # File might still be in use

                                if clicked:
                                    if st.session_state.edit_mode:
                                        st.session_state.selected_button = (r, c)
                                        st.rerun()
                                    else:
                                        # Execute Action
                                        if btn_data:
                                            msg = executor.execute_action(
                                                btn_data.get("type"),
                                                btn_data.get("action"),
                                            )
                                            st.toast(msg)
                        else:
                            # Fallback to regular button if no icon found
                            clicked = st.button(
                                label,
                                key=f"btn_{r}_{c}",
                                use_container_width=True,
                                type=btn_display_type,
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
                        # Regular button for non-app actions
                        clicked = st.button(
                            label,
                            key=f"btn_{r}_{c}",
                            use_container_width=True,
                            type=btn_display_type,
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
    # Header removed per user request

    # --- Mappings & Constants ---
    BASIC_CHARS_DISPLAY = [c.upper() for c in string.ascii_lowercase] + list(
        string.digits
    )
    BASIC_CHARS_MAP = {c.upper(): c for c in string.ascii_lowercase}
    BASIC_CHARS_MAP.update({d: d for d in string.digits})  # Digits map to themselves

    EXTENDED_CHARS = [
        "⌃ ctrl",
        "⇧ shift",
        "⌥ alt",
        "⌘ cmd",
        "↵ enter",
        "⎋ esc",
        "⇥ tab",
        "␣ space",
        "⌫ backspace",
        "⌦ delete",
        "↑ up",
        "↓ down",
        "← left",
        "→ right",
        "⇪ capslock",
    ] + [f"F{i}" for i in range(1, 13)]

    # Mapping from display name to internal key name
    EXTENDED_CHAR_MAP = {
        "⌃ ctrl": "ctrl",
        "⇧ shift": "shift",
        "⌥ alt": "alt",
        "⌘ cmd": "cmd",
        "↵ enter": "enter",
        "⎋ esc": "esc",
        "⇥ tab": "tab",
        "␣ space": "space",
        "⌫ backspace": "backspace",
        "⌦ delete": "delete",
        "↑ up": "up",
        "↓ down": "down",
        "← left": "left",
        "→ right": "right",
        "⇪ capslock": "capslock",
    }
    # Add function keys
    for i in range(1, 13):
        EXTENDED_CHAR_MAP[f"F{i}"] = f"f{i}"

    # Reverse mapping for initialization
    EXTENDED_CHAR_REVERSE = {v: k for k, v in EXTENDED_CHAR_MAP.items()}

    MEDIA_MAP = {
        "playpause": ":material/play_arrow: Play/Pause",
        "volumemute": ":material/volume_off: Mute",
        "volumeup": ":material/volume_up: Vol Up",
        "volumedown": ":material/volume_down: Vol Down",
        "nexttrack": ":material/skip_next: Next",
        "prevtrack": ":material/skip_previous: Prev",
    }
    MEDIA_REVERSE = {v: k for k, v in MEDIA_MAP.items()}

    MOUSE_MAP = {
        "left_click": "Left Click",
        "right_click": "Right Click",
        "middle_click": "Middle Click",
        "double_left_click": "Double Click",
    }
    MOUSE_REVERSE = {v: k for k, v in MOUSE_MAP.items()}

    SCRIPTS_LIST = config.list_scripts()
    APPS_LIST = list(APPS_DICT.keys())
    # Create reverse map for apps (command to name)
    APPS_REVERSE = {}
    for app_name, app_data in APPS_DICT.items():
        if isinstance(app_data, dict) and "command" in app_data:
            APPS_REVERSE[app_data["command"]] = app_name

    # --- State Initialization ---
    # Ensure draft variables exist even if we are re-entering this block without a selection change
    # (e.g. after a code reload or if they were somehow cleared)
    if "draft_basic" not in st.session_state:
        st.session_state.draft_basic = []
    if "draft_extended" not in st.session_state:
        st.session_state.draft_extended = []
    if "draft_script" not in st.session_state:
        st.session_state.draft_script = None
    if "draft_media" not in st.session_state:
        st.session_state.draft_media = None
    if "draft_mouse" not in st.session_state:
        st.session_state.draft_mouse = None
    if "draft_app" not in st.session_state:
        st.session_state.draft_app = None
    if "draft_label" not in st.session_state:
        st.session_state.draft_label = btn_data.get("label", "")

    # We use 'last_selected_btn_id' to detect when the user clicked a different button
    # and re-initialize the draft state from the config.
    current_selection_id = f"sel_{r}_{c}"
    if st.session_state.get("last_selection_id") != current_selection_id:
        st.session_state.last_selection_id = current_selection_id

        # Initialize Draft Values from current button data
        st.session_state.draft_basic = []
        st.session_state.draft_extended = []
        st.session_state.draft_script = None
        st.session_state.draft_media = None  # Single selection
        st.session_state.draft_mouse = None
        st.session_state.draft_app = None
        st.session_state.draft_label = btn_data.get("label", "")

        curr_type = btn_data.get("type", "hotkey")
        curr_action = btn_data.get("action", "")

        if curr_type == "script" and curr_action in SCRIPTS_LIST:
            st.session_state.draft_script = curr_action
        elif curr_type == "mouse" and curr_action in MOUSE_MAP:
            st.session_state.draft_mouse = MOUSE_MAP[curr_action]
        elif curr_type == "app":
            # Try to find app name from command/path
            if curr_action in APPS_REVERSE:
                st.session_state.draft_app = APPS_REVERSE[curr_action]
            else:
                # If exact path not found (maybe app updated path), show raw or closest match?
                # For now, just leave empty or maybe check value match logic
                pass
        elif curr_type == "hotkey":
            # Check for Media
            keys = curr_action.split("+")
            # If single key and in media map
            if len(keys) == 1 and keys[0] in MEDIA_MAP:
                st.session_state.draft_media = MEDIA_MAP[keys[0]]
            else:
                # Normal hotkeys
                for k in keys:
                    k = k.strip().lower()
                    if k.upper() in BASIC_CHARS_MAP:
                        st.session_state.draft_basic.append(k.upper())
                    elif k in EXTENDED_CHAR_REVERSE:
                        st.session_state.draft_extended.append(EXTENDED_CHAR_REVERSE[k])

    # --- Callbacks ---
    def on_keys_change():
        # Clear other selections when keys change
        st.session_state.draft_script = None
        st.session_state.draft_media = None
        st.session_state.draft_mouse = None
        st.session_state.draft_app = None
        update_label_from_action()

    def on_script_change():
        # Clear other selections when script changes
        if st.session_state.draft_script:
            st.session_state.draft_basic = []
            st.session_state.draft_extended = []
            st.session_state.draft_media = None
            st.session_state.draft_mouse = None
            st.session_state.draft_app = None
            update_label_from_action()

    def on_media_change():
        # Clear other selections when media changes
        if st.session_state.draft_media:
            st.session_state.draft_basic = []
            st.session_state.draft_extended = []
            st.session_state.draft_script = None
            st.session_state.draft_mouse = None
            st.session_state.draft_app = None
            update_label_from_action()

    def on_mouse_change():
        # Clear other selections when mouse changes
        if st.session_state.draft_mouse:
            st.session_state.draft_basic = []
            st.session_state.draft_extended = []
            st.session_state.draft_script = None
            st.session_state.draft_media = None
            st.session_state.draft_app = None
            update_label_from_action()

    def on_app_change():
        # Clear other selections when app changes
        if st.session_state.draft_app:
            st.session_state.draft_basic = []
            st.session_state.draft_extended = []
            st.session_state.draft_script = None
            st.session_state.draft_media = None
            st.session_state.draft_mouse = None
            update_label_from_action()

    def update_label_from_action():
        # Optional: Auto-update label if it's empty or matches previous action
        # For now, we'll leave this manual unless user specifically requested auto-labeling logic
        pass

    # --- Computed Action String ---
    current_action_str = ""
    if st.session_state.draft_script:
        current_action_str = f"Script: {st.session_state.draft_script}"
    elif st.session_state.draft_app:
        current_action_str = f"App: {st.session_state.draft_app}"
    elif st.session_state.draft_media:
        current_action_str = f"Media: {st.session_state.draft_media}"
    elif st.session_state.draft_mouse:
        current_action_str = f"Mouse: {st.session_state.draft_mouse}"
    else:
        # Hotkeys
        keys = []
        # Add modifiers first
        modifiers = ["ctrl", "shift", "alt", "cmd"]
        sel_ext = st.session_state.draft_extended or []
        sel_basic = st.session_state.draft_basic or []

        sel_mods = [
            EXTENDED_CHAR_MAP.get(k, k)
            for k in sel_ext
            if EXTENDED_CHAR_MAP.get(k, k) in modifiers
        ]
        sel_other_ext = [
            EXTENDED_CHAR_MAP.get(k, k)
            for k in sel_ext
            if EXTENDED_CHAR_MAP.get(k, k) not in modifiers
        ]

        keys.extend(sel_mods)
        # Convert display basic chars back to internal (lowercase)
        keys.extend([BASIC_CHARS_MAP[c] for c in sel_basic])
        keys.extend(sel_other_ext)

        if keys:
            current_action_str = "+".join(keys)

    # --- UI Layout ---
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([3, 3, 1, 1], vertical_alignment="bottom")
        with c1:
            st.session_state.draft_label = st.text_input(
                "Button Label", value=st.session_state.draft_label
            )
        with c2:
            st.text_input(
                "Current Action",
                value=current_action_str,
                disabled=True,
                help="Automatically updated based on selections below.",
            )

        with c3:
            if st.button("Save", type="primary", use_container_width=True):
                # Construct final payload
                final_type = "hotkey"
                final_payload = ""
                final_label = st.session_state.draft_label

                if st.session_state.draft_script:
                    final_type = "script"
                    final_payload = st.session_state.draft_script
                    if not final_label:
                        final_label = final_payload
                elif st.session_state.draft_app:
                    final_type = "app"
                    # Payload is the command from the rich APPS_DICT
                    app_data = APPS_DICT.get(st.session_state.draft_app, {})
                    final_payload = app_data.get("command", st.session_state.draft_app)

                    if not final_label:
                        final_label = st.session_state.draft_app
                elif st.session_state.draft_mouse:
                    final_type = "mouse"
                    final_payload = MOUSE_REVERSE[st.session_state.draft_mouse]
                    if not final_label:
                        final_label = st.session_state.draft_mouse
                elif st.session_state.draft_media:
                    final_type = (
                        "hotkey"  # Media is handled as hotkey in backend currently?
                    )
                    # Check executor.py... Yes, MEDIA keys are in KEY_MAP.
                    # Wait, backend executor.py has KEY_MAP which includes media keys.
                    # So type is "hotkey", payload is "volumemute" etc.
                    final_payload = MEDIA_REVERSE[st.session_state.draft_media]
                    if not final_label:
                        final_label = st.session_state.draft_media
                else:
                    # Hotkeys calculation (duplicated from above, but safe)
                    keys = []
                    modifiers = ["ctrl", "shift", "alt", "cmd"]
                    sel_ext = st.session_state.draft_extended or []
                    sel_basic = st.session_state.draft_basic or []

                    sel_mods = [
                        EXTENDED_CHAR_MAP.get(k, k)
                        for k in sel_ext
                        if EXTENDED_CHAR_MAP.get(k, k) in modifiers
                    ]
                    sel_other_ext = [
                        EXTENDED_CHAR_MAP.get(k, k)
                        for k in sel_ext
                        if EXTENDED_CHAR_MAP.get(k, k) not in modifiers
                    ]

                    keys.extend(sel_mods)
                    keys.extend([BASIC_CHARS_MAP[c] for c in sel_basic])
                    keys.extend(sel_other_ext)

                    if keys:
                        final_payload = "+".join(keys)
                        if not final_label:
                            final_label = final_payload

                # Save
                if btn_id not in layout["buttons"]:
                    layout["buttons"][btn_id] = {}

                layout["buttons"][btn_id] = {
                    "row": r,
                    "col": c,
                    "label": final_label,
                    "type": final_type,
                    "action": final_payload,
                }
                config.save_layout(st.session_state.current_layout_name, layout)
                st.toast("Button Saved!")
                st.rerun()

        with c4:
            if st.button("Clear", use_container_width=True):
                if btn_id in layout["buttons"]:
                    del layout["buttons"][btn_id]
                    config.save_layout(st.session_state.current_layout_name, layout)

                # Clear all draft session state
                st.session_state.draft_basic = []
                st.session_state.draft_extended = []
                st.session_state.draft_script = None
                st.session_state.draft_media = None
                st.session_state.draft_mouse = None
                st.session_state.draft_app = None
                st.session_state.draft_label = ""

                st.rerun()

        # 1. Basic Characters
        with st.expander("Basic Characters"):
            st.pills(
                "Select Characters",
                BASIC_CHARS_DISPLAY,
                selection_mode="multi",
                key="draft_basic",
                on_change=on_keys_change,
            )

        # 2. Extended Characters
        with st.expander("Extended Characters"):
            st.pills(
                "Select Special Keys",
                EXTENDED_CHARS,
                selection_mode="multi",
                key="draft_extended",
                on_change=on_keys_change,
            )

        # 3. Functions (Scripts)
        with st.expander("Functions (Scripts)"):
            if SCRIPTS_LIST:
                st.pills(
                    "Select Script",
                    SCRIPTS_LIST,
                    selection_mode="single",
                    key="draft_script",
                    on_change=on_script_change,
                )
            else:
                st.warning("No scripts found in scripts/ directory")

        # 4. Applications (New)
        with st.expander("Applications"):
            if APPS_LIST:
                # Import the image button component
                from st_image_button import st_image_button
                import tempfile

                # Create a 3-column grid for app selection
                app_cols = st.columns(3)
                for i, app_name in enumerate(APPS_LIST):
                    with app_cols[i % 3]:
                        app_data = APPS_DICT[app_name]

                        # Create image button if icon available
                        if app_data.get("icon_bytes"):
                            # Save icon bytes to temporary PNG file
                            with tempfile.NamedTemporaryFile(
                                suffix=".png", delete=False
                            ) as tmp:
                                tmp.write(app_data["icon_bytes"])
                                tmp.flush()

                                # Use image button component
                                clicked = st_image_button(
                                    text=app_name,  # Button text/title
                                    image=tmp.name,  # Path to temp image file
                                    width="48px",  # Size as requested
                                    variant="outlined",  # Clean outlined style
                                    key=f"app_img_btn_{app_name}",
                                )

                                # Clean up temp file after a delay (can't delete immediately due to Streamlit's async nature)
                                # Streamlit will handle cleanup on rerun
                                try:
                                    os.unlink(tmp.name)
                                except:
                                    pass  # File might still be in use

                                if clicked:
                                    # Use a safer approach - clear the session state first
                                    if "draft_basic" in st.session_state:
                                        st.session_state.pop("draft_basic")
                                    if "draft_extended" in st.session_state:
                                        st.session_state.pop("draft_extended")
                                    if "draft_script" in st.session_state:
                                        st.session_state.pop("draft_script")
                                    if "draft_media" in st.session_state:
                                        st.session_state.pop("draft_media")
                                    if "draft_mouse" in st.session_state:
                                        st.session_state.pop("draft_mouse")

                                    st.session_state.draft_app = app_name
                                    st.rerun()
                        else:
                            # Fallback to regular button if no icon
                            if st.button(
                                app_name,
                                key=f"app_select_{app_name}",
                                use_container_width=True,
                            ):
                                # Use a safer approach - clear the session state first
                                if "draft_basic" in st.session_state:
                                    st.session_state.pop("draft_basic")
                                if "draft_extended" in st.session_state:
                                    st.session_state.pop("draft_extended")
                                if "draft_script" in st.session_state:
                                    st.session_state.pop("draft_script")
                                if "draft_media" in st.session_state:
                                    st.session_state.pop("draft_media")
                                if "draft_mouse" in st.session_state:
                                    st.session_state.pop("draft_mouse")

                                st.session_state.draft_app = app_name
                                st.rerun()
            else:
                st.warning("No applications found.")

        # 5. Media and Audio Control
        with st.expander("Media & Audio"):
            st.pills(
                "Media Controls",
                list(MEDIA_MAP.values()),
                selection_mode="single",  # Changed to single per requirement
                key="draft_media",
                on_change=on_media_change,
            )

        # 6. Mouse
        with st.expander("Mouse"):
            st.pills(
                "Mouse Actions",
                list(MOUSE_MAP.values()),
                selection_mode="single",
                key="draft_mouse",
                on_change=on_mouse_change,
            )

# --- Footer / Info ---
if st.session_state.edit_mode:
    layout_name = layout.get("name", "Default")  # Add default value
    st.info(f"Layout: {layout_name} | Size: {rows}x{cols}")
