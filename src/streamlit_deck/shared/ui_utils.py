"""
Shared UI utilities for Streamlit Deck.
"""

import base64


# Utility functions for icon handling
def is_svg_data(data: bytes) -> bool:
    """Check if data is SVG (starts with XML or SVG tag)."""
    return data.startswith(b"<?xml") or data.startswith(b"<svg")


def get_icon_display(icon_bytes: bytes, size: int = 48) -> str:
    """Get HTML for displaying icon - SVG inline or PNG base64 img tag."""
    if not icon_bytes:
        return ""

    if is_svg_data(icon_bytes):
        # SVG can be embedded directly with proper sizing
        svg_content = icon_bytes.decode("utf-8", errors="ignore")
        return f'<div style="width: {size}px; height: {size}px; display: flex; align-items: center; justify-content: center;">{svg_content}</div>'
    else:
        # PNG needs base64 encoding
        b64_encoded = base64.b64encode(icon_bytes).decode("utf-8")
        return f'<img src="data:image/png;base64,{b64_encoded}" style="width: {size}px; height: {size}px;" alt="icon">'


def display_icon_in_column(icon_bytes: bytes, size: int = 48):
    """Display icon in a column with vertical centering."""
    if icon_bytes:
        icon_html = get_icon_display(icon_bytes, size)
        # Wrap in a container with centering class
        centered_html = f'<div class="icon-container">{icon_html}</div>'
        import streamlit as st

        st.markdown(centered_html, unsafe_allow_html=True)
    else:
        # Empty placeholder with same height for alignment
        import streamlit as st

        st.markdown('<div class="icon-container"></div>', unsafe_allow_html=True)
