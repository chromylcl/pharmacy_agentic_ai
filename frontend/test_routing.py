"""
test_routing.py
----------------
Tests quick_actions, emergency_detector, emergency_alert,
drug_detector, and prescription_upload all together.
Run with: streamlit run test_routing.py
Place in frontend/ root. Delete after testing.
"""

import streamlit as st
import sys, os, uuid
sys.path.insert(0, os.path.dirname(__file__))

from components.quick_actions        import render_quick_actions
from components.emergency_alert      import render_emergency_alert
from components.prescription_upload  import render_prescription_upload
from utils.emergency_detector        import is_emergency
from utils.drug_detector             import is_restricted_drug, get_detected_drug

st.set_page_config(
    page_title="Routing Test — Pharmacy Assistant Demo",
    page_icon="🧪",
    layout="centered",
)

# ── Minimal session state ─────────────────────────────────────────────────────
if "patient_name"          not in st.session_state:
    st.session_state.patient_name          = "Guest Patient"
if "ui_phase"              not in st.session_state:
    st.session_state.ui_phase              = "chatting"
if "is_first_message"      not in st.session_state:
    st.session_state.is_first_message      = True
if "messages"              not in st.session_state:
    st.session_state.messages              = []
if "pending_prescription"  not in st.session_state:
    st.session_state.pending_prescription  = None
if "langfuse_trace_id"     not in st.session_state:
    st.session_state.langfuse_trace_id     = str(uuid.uuid4())
if "consultation_summary"  not in st.session_state:
    st.session_state.consultation_summary  = []

# ── Test controls in sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.title("🧪 Test Controls")
    st.divider()

    st.markdown("**Force ui_phase:**")
    if st.button("💬 Normal chat (quick actions)", use_container_width=True):
        st.session_state.ui_phase         = "chatting"
        st.session_state.is_first_message = True
        st.rerun()

    if st.button("🚨 Emergency alert", use_container_width=True):
        st.session_state.ui_phase = "emergency_alert"
        st.rerun()

    if st.button("📋 Prescription upload", use_container_width=True):
        st.session_state.ui_phase            = "prescription_upload"
        st.session_state.pending_prescription = "oxycodone"
        st.rerun()

    st.divider()
    st.markdown("**Test detectors:**")
    test_input = st.text_input("Type a message to test:", value="I need oxycodone")
    if st.button("Run detectors"):
        st.write(f"is_emergency: `{is_emergency(test_input)}`")
        st.write(f"is_restricted_drug: `{is_restricted_drug(test_input)}`")
        st.write(f"detected_drug: `{get_detected_drug(test_input)}`")

    st.divider()
    st.markdown(f"**ui_phase:** `{st.session_state.ui_phase}`")
    st.markdown(f"**is_first_message:** `{st.session_state.is_first_message}`")
    st.markdown(f"**pending_prescription:** `{st.session_state.pending_prescription}`")

# ── Main area — routing logic (mirrors app.py) ────────────────────────────────
if st.session_state.ui_phase == "emergency_alert":
    render_emergency_alert("I think I'm having a chest pain")
    st.stop()

elif st.session_state.ui_phase == "prescription_upload":
    render_prescription_upload()
    st.stop()

else:
    st.title("🧪 Routing Test — Normal Chat")
    st.caption("Quick actions show below on fresh session. Use sidebar to switch states.")
    st.divider()

    clicked = render_quick_actions()
    if clicked:
        st.session_state.is_first_message = False
        st.success(f"✅ Quick action clicked: '{clicked}'")
        st.info("In app.py this would trigger handle_user_message(clicked)")