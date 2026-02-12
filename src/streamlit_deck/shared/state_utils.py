"""
Shared utilities for state management in Streamlit Deck.
"""

import streamlit as st


def clear_draft_state():
    """Clear all draft state variables for button editing."""
    st.session_state.draft_basic = []
    st.session_state.draft_extended = []
    st.session_state.draft_script = None
    st.session_state.draft_media = None
    st.session_state.draft_mouse = None
    st.session_state.draft_app = None
    st.session_state.draft_label = ""


def init_draft_state():
    """Initialize draft state variables if they don't exist."""
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
        st.session_state.draft_label = ""
