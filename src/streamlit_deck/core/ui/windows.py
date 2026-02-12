"""
UI components for displaying and switching between open windows.
"""

import streamlit as st


def render_open_windows(apps_handler):
    """
    Render the open windows footer section.
    """
    st.markdown(
        """
    <style>
    .open-windows-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: var(--background-color);
        padding: 10px;
        border-top: 1px solid var(--secondary-background-color);
        z-index: 1000;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown('<div class="open-windows-footer">', unsafe_allow_html=True)
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
                            app_name = window_info["app_name"]
                            is_active = window_info["is_active"]

                            button_label = f"{app_name} {'●' if is_active else ''}"

                            # Truncate long titles
                            if len(button_label) > 15:
                                button_label = button_label[:12] + "..."

                            button_type = "primary" if is_active else "secondary"

                            if st.button(
                                button_label,
                                key=f"window_{window_idx}",
                                use_container_width=True,
                                type=button_type,
                            ):
                                msg = apps_handler.switch_to_app(app_name)
                                st.toast(msg)
        else:
            st.info("No open windows detected. This feature is macOS-only.")
            if debug:
                st.code(f"Debug: {debug}", language="text")
        st.markdown("</div>", unsafe_allow_html=True)
