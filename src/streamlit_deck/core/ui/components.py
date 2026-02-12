"""
Reusable UI components for Streamlit Deck.
"""

import streamlit as st
from ...shared.ui_utils import display_icon_in_column


def render_icon_button(icon_bytes: bytes, label: str, key: str, **kwargs) -> bool:
    """
    Render a button with an icon and label in a mini-row layout.

    Args:
        icon_bytes: Icon data to display.
        label: Button label.
        key: Unique key for the button.
        **kwargs: Additional arguments for st.button.

    Returns:
        True if the button was clicked.
    """
    # Create mini-row within each grid cell: icon + button label
    cell_cols = st.columns(
        [1, 2], gap="xxsmall"
    )  # Icon column wider, minimal gap for closer spacing

    with cell_cols[0]:
        # Display icon in first mini-column
        display_icon_in_column(icon_bytes, size=40)

    with cell_cols[1]:
        return st.button(label, key=key, width="stretch", **kwargs)
