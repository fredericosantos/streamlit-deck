import streamlit as st
import sys
from streamlit_deck.core.backend.config import list_scripts, save_layout
from streamlit_deck.platform import get_mappings
from streamlit_deck.shared.app_utils import build_apps_reverse_map
from streamlit_deck.shared.state_utils import clear_draft_state, init_draft_state
from streamlit_deck.shared.hotkey_utils import build_hotkey_string
from streamlit_deck.core.ui.components import render_icon_button

# --- Constants ---

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


def render_editor(layout, r, c, btn_id, btn_data, APPS_DICT):
    # Get OS-specific mappings
    mappings = get_mappings()

    BASIC_CHARS_MAP = mappings.basic_chars_map
    EXTENDED_CHAR_MAP = mappings.extended_char_map

    # Reverse mapping for initialization
    EXTENDED_CHAR_REVERSE = {v: k for k, v in EXTENDED_CHAR_MAP.items()}

    SCRIPTS_LIST = list_scripts()
    APPS_LIST = list(APPS_DICT.keys())
    APPS_REVERSE = build_apps_reverse_map(APPS_DICT)

    # --- State Initialization ---
    init_draft_state()

    # OS Mode default
    if "os_mode" not in st.session_state:
        st.session_state.os_mode = "macos" if sys.platform == "darwin" else "linux"

    # --- OS Mode Toggle ---
    st.selectbox("OS Mode", ["macos", "linux"], key="os_mode")

    current_selection_id = f"sel_{r}_{c}"
    if st.session_state.get("last_selection_id") != current_selection_id:
        st.session_state.last_selection_id = current_selection_id
        clear_draft_state()
        st.session_state.draft_label = btn_data.get("label", "")

        curr_type = btn_data.get("type", "hotkey")
        curr_action = btn_data.get("action", "")

        if curr_type == "script" and curr_action in SCRIPTS_LIST:
            st.session_state.draft_script = curr_action
        elif curr_type == "mouse" and curr_action in MOUSE_MAP:
            st.session_state.draft_mouse = MOUSE_MAP[curr_action]
        elif curr_type == "app":
            if curr_action in APPS_REVERSE:
                st.session_state.draft_app = APPS_REVERSE[curr_action]
        elif curr_type == "hotkey":
            keys = curr_action.split("+")
            if len(keys) == 1 and keys[0] in MEDIA_MAP:
                st.session_state.draft_media = MEDIA_MAP[keys[0]]
            else:
                for k in keys:
                    k = k.strip().lower()
                    if k.upper() in BASIC_CHARS_MAP:
                        st.session_state.draft_basic.append(k.upper())
                    elif k in EXTENDED_CHAR_REVERSE:
                        st.session_state.draft_extended.append(EXTENDED_CHAR_REVERSE[k])

    # --- Callbacks ---
    def on_selection_change(key_to_keep):
        """Unified callback to clear other draft states when one changes."""
        for state_key in [
            "draft_basic",
            "draft_extended",
            "draft_script",
            "draft_media",
            "draft_mouse",
            "draft_app",
        ]:
            if state_key != key_to_keep and state_key in st.session_state:
                if isinstance(st.session_state[state_key], list):
                    st.session_state[state_key] = []
                else:
                    st.session_state[state_key] = None

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
        current_action_str = build_hotkey_string(
            st.session_state.draft_basic,
            st.session_state.draft_extended,
            BASIC_CHARS_MAP,
            EXTENDED_CHAR_MAP,
        )

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
            if st.button(
                "Save", type="primary", use_container_width=True, shortcut="Ctrl+S"
            ):
                final_type = "hotkey"
                final_payload = ""
                final_label = st.session_state.draft_label

                if st.session_state.draft_script:
                    final_type = "script"
                    final_payload = st.session_state.draft_script
                elif st.session_state.draft_app:
                    final_type = "app"
                    app_data = APPS_DICT.get(st.session_state.draft_app, {})
                    final_payload = app_data.get("command", st.session_state.draft_app)
                elif st.session_state.draft_mouse:
                    final_type = "mouse"
                    final_payload = MOUSE_REVERSE[st.session_state.draft_mouse]
                elif st.session_state.draft_media:
                    final_type = "hotkey"
                    final_payload = MEDIA_REVERSE[st.session_state.draft_media]
                else:
                    final_payload = build_hotkey_string(
                        st.session_state.draft_basic,
                        st.session_state.draft_extended,
                        BASIC_CHARS_MAP,
                        EXTENDED_CHAR_MAP,
                    )

                if not final_label:
                    final_label = (
                        st.session_state.draft_app
                        or st.session_state.draft_script
                        or st.session_state.draft_mouse
                        or st.session_state.draft_media
                        or final_payload
                    )

                layout["buttons"][btn_id] = {
                    "row": r,
                    "col": c,
                    "label": final_label,
                    "type": final_type,
                    "action": final_payload,
                }
                save_layout(st.session_state.current_layout_name, layout)
                st.toast("Button Saved!")
                st.rerun()

        with c4:
            if st.button("Clear", use_container_width=True, shortcut="Delete"):
                if btn_id in layout["buttons"]:
                    del layout["buttons"][btn_id]
                    save_layout(st.session_state.current_layout_name, layout)
                clear_draft_state()
                st.rerun()

        # 1. Basic Characters
        with st.expander("Basic Characters"):
            st.pills(
                "Select Characters",
                mappings.basic_chars_display,
                selection_mode="multi",
                key="draft_basic",
                on_change=on_selection_change,
                args=("draft_basic",),
            )

        # 2. Extended Characters
        with st.expander("Extended Characters"):
            st.pills(
                "Select Special Keys",
                mappings.extended_chars,
                selection_mode="multi",
                key="draft_extended",
                on_change=on_selection_change,
                args=("draft_extended",),
            )

        # 3. Functions (Scripts)
        with st.expander("Functions (Scripts)"):
            if SCRIPTS_LIST:
                st.pills(
                    "Select Script",
                    SCRIPTS_LIST,
                    selection_mode="single",
                    key="draft_script",
                    on_change=on_selection_change,
                    args=("draft_script",),
                )
            else:
                st.warning("No scripts found in scripts/ directory")

        # 4. Applications
        with st.expander("Applications"):
            if APPS_LIST:
                num_cols = 3
                app_rows = (len(APPS_LIST) + num_cols - 1) // num_cols
                for app_row in range(app_rows):
                    app_cols = st.columns(num_cols)
                    for col_idx in range(num_cols):
                        app_idx = app_row * num_cols + col_idx
                        if app_idx < len(APPS_LIST):
                            app_name = APPS_LIST[app_idx]
                            app_data = APPS_DICT[app_name]
                            with app_cols[col_idx]:
                                if render_icon_button(
                                    app_data.get("icon_bytes"),
                                    app_name,
                                    f"ed_app_{app_name}",
                                ):
                                    on_selection_change("draft_app")
                                    st.session_state.draft_app = app_name
                                    st.rerun()
            else:
                st.warning("No applications found.")

        # 5. Media and Audio Control
        with st.expander("Media & Audio"):
            st.pills(
                "Media Controls",
                list(MEDIA_MAP.values()),
                selection_mode="single",
                key="draft_media",
                on_change=on_selection_change,
                args=("draft_media",),
            )

        # 6. Mouse
        with st.expander("Mouse"):
            st.pills(
                "Mouse Actions",
                list(MOUSE_MAP.values()),
                selection_mode="single",
                key="draft_mouse",
                on_change=on_selection_change,
                args=("draft_mouse",),
            )
