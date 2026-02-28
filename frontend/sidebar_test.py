"""
test_sidebar.py
----------------
Standalone test for components/sidebar.py
Run with: streamlit run test_sidebar.py
Place in frontend/ root folder. Delete after testing.
"""

import streamlit as st
import sys, os, uuid
sys.path.insert(0, os.path.dirname(__file__))

from components.sidebar import render_sidebar

st.set_page_config(
    page_title="Sidebar Test — Pharmacy Assistant",
    page_icon="💊",
    layout="wide",
)

# Minimal session state
if "patient_name" not in st.session_state:
    st.session_state.patient_name = "Guest Patient"
if "ui_phase" not in st.session_state:
    st.session_state.ui_phase = "chatting"
if "is_first_message" not in st.session_state:
    st.session_state.is_first_message = True
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hello! I'm Pharmacy Assistant."},
        {"role": "user",      "content": "I have a headache."},
        {"role": "assistant", "content": "Try paracetamol 500mg."},
    ]
if "pending_prescription" not in st.session_state:
    st.session_state.pending_prescription = None
if "langfuse_trace_id" not in st.session_state:
    st.session_state.langfuse_trace_id = str(uuid.uuid4())
if "consultation_summary" not in st.session_state:
    st.session_state.consultation_summary = []

# Render sidebar
render_sidebar()

# Main area placeholder
st.title("🧪 sidebar.py — Component Test")
st.caption("Check the left sidebar.")
st.divider()
st.info("The main chat area will go here in app.py")
st.markdown(f"**patient_name:** `{st.session_state.patient_name}`")
st.markdown(f"**ui_phase:** `{st.session_state.ui_phase}`")
st.markdown(f"**is_first_message:** `{st.session_state.is_first_message}`")
st.markdown(f"**messages count:** `{len(st.session_state.messages)}`")