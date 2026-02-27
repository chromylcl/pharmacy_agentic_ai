"""
test_api_client.py
-------------------
Standalone test for services/api_client.py
Run with: streamlit run test_api_client.py
Place in frontend/ root. Delete after testing.

Tests all 5 functions with dummy data.
When backend is ready, flip the BACKEND_READY flag to True
and it will test real endpoints instead.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from services.api_client import (
    call_pharmacist,
    call_safety,
    call_fulfillment,
    call_final_streamed,
    call_transcribe,
    call_refill_check,
    safe_call,
)

st.set_page_config(
    page_title="API Client Test — Atharva",
    page_icon="🔌",
    layout="centered",
)

st.title("🔌 api_client.py — Function Test")
st.caption("Tests all API functions. Currently using dummy data — no backend needed.")
st.divider()

user_input = st.text_input(
    "Test message:",
    value="I have a headache and mild fever.",
)

# ── Individual function tests ─────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🩺 Pharmacist", use_container_width=True):
        with st.spinner("Calling pharmacist..."):
            result = safe_call(call_pharmacist, user_input)
        st.text_area("Result:", result, height=150)

with col2:
    if st.button("🛡️ Safety", use_container_width=True):
        with st.spinner("Calling safety..."):
            result = safe_call(call_safety, user_input)
        st.text_area("Result:", result, height=150)

with col3:
    if st.button("📦 Fulfillment", use_container_width=True):
        with st.spinner("Calling fulfillment..."):
            result = safe_call(call_fulfillment, user_input)
        st.text_area("Result:", result, height=150)

st.divider()

# ── Streaming test ────────────────────────────────────────────────────────────
st.subheader("💬 Streaming Response Test")
if st.button("▶️ Stream Final Response", use_container_width=True):
    placeholder = st.empty()
    full = ""
    for chunk in call_final_streamed(user_input):
        full += chunk
        placeholder.markdown(full + "▌")
    placeholder.markdown(full)
    st.success(f"✅ Stream complete. {len(full)} characters received.")

st.divider()

# ── Refill check test ─────────────────────────────────────────────────────────
st.subheader("📊 Refill Check Test")
if st.button("Check Refill Risk", use_container_width=True):
    result = safe_call(call_refill_check, "patient_001", "paracetamol")
    st.json(result)

st.divider()

# ── Voice transcription test ──────────────────────────────────────────────────
st.subheader("🎙️ Voice Transcription Test")
st.caption("Returns dummy text for now — swap in real audio when backend is ready.")
if st.button("Simulate Transcription", use_container_width=True):
    result = safe_call(call_transcribe, b"fake_audio_bytes")
    st.success(f"Transcribed: '{result}'")