"""
test_chat.py
------------
Standalone test for components/chat.py
Run with: streamlit run test_chat.py
Place this file in your frontend/ root folder.
"""

import streamlit as st
import sys
import os

# Make sure components/ is importable from frontend/
sys.path.insert(0, os.path.dirname(__file__))

from components.chat import render_chat_history, render_streaming_response


# ── Fake session state setup ──────────────────────────────────────────────────
def init_fake_session():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            # Greeting from assistant (no agent logs)
            {
                "role": "assistant",
                "content": "👋 Hello! I'm Atharva, your AI pharmacy assistant. How can I help you today?",
            },
            # User message
            {
                "role": "user",
                "content": "I have a headache and mild fever. What can I take?",
            },
            # Assistant reply WITH agent logs
            {
                "role": "assistant",
                "content": (
                    "Based on your symptoms, **paracetamol (500mg)** is a safe first option. "
                    "Take one tablet every 4–6 hours as needed, and stay well hydrated. "
                    "If fever exceeds 39°C or persists beyond 48 hours, please consult a doctor."
                ),
                "agent_logs": [
                    {
                        "agent": "🩺 Pharmacist",
                        "log": (
                            "Patient reports: headache + mild fever.\n"
                            "Recommended: Paracetamol 500mg — OTC, no prescription required.\n"
                            "Dosage: 1 tablet every 4–6 hours. Max 4 tablets/day.\n"
                            "No known contraindications for general adult population."
                        ),
                    },
                    {
                        "agent": "🛡️ Safety",
                        "log": (
                            "Drug interaction check: No active medications on file.\n"
                            "Paracetamol flagged SAFE at standard dosage.\n"
                            "Warning: Avoid alcohol. Hepatotoxic in overdose — do not exceed 4g/day."
                        ),
                    },
                    {
                        "agent": "📦 Fulfillment",
                        "log": (
                            "Inventory check: Paracetamol 500mg — IN STOCK ✅\n"
                            "PDC Score: N/A (new medication, no refill history).\n"
                            "Estimated supply for standard 3-day course: 12 tablets."
                        ),
                    },
                ],
            },
            # Another user message
            {
                "role": "user",
                "content": "Is it safe to take ibuprofen at the same time?",
            },
            # Assistant reply with 2 agent logs
            {
                "role": "assistant",
                "content": (
                    "Yes, **paracetamol and ibuprofen can be taken together** — they work differently "
                    "and don't interact. However, take ibuprofen **with food** to avoid stomach irritation. "
                    "Alternate them every 3 hours for better fever control."
                ),
                "agent_logs": [
                    {
                        "agent": "🛡️ Safety",
                        "log": (
                            "Combination check: Paracetamol + Ibuprofen.\n"
                            "Result: SAFE — different mechanisms, no harmful interaction.\n"
                            "Caution: Ibuprofen is an NSAID — avoid on empty stomach.\n"
                            "Contraindicated in: renal impairment, peptic ulcer disease, pregnancy (3rd trimester)."
                        ),
                    },
                    {
                        "agent": "🩺 Pharmacist",
                        "log": (
                            "Alternating regimen suggestion:\n"
                            "  Hour 0  → Paracetamol 500mg\n"
                            "  Hour 3  → Ibuprofen 400mg (with food)\n"
                            "  Hour 6  → Paracetamol 500mg\n"
                            "This avoids exceeding individual drug limits while maintaining coverage."
                        ),
                    },
                ],
            },
        ]


# ── Fake streaming generator ──────────────────────────────────────────────────
def fake_stream():
    """Simulates a backend stream token by token."""
    import time
    tokens = [
        "Sure! ", "Based on your ", "current situation, ",
        "I'd recommend ", "monitoring your ", "temperature every ",
        "4 hours. ", "If it spikes ", "above 39°C, ",
        "please seek ", "medical attention ", "immediately. 🌡️"
    ]
    for token in tokens:
        time.sleep(0.08)
        yield token


# ── Page layout ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Chat Component Test — Atharva",
    page_icon="💊",
    layout="centered",
)

st.title("🧪 chat.py — Component Test")
st.caption("This is a test harness. No backend needed. All data is mocked.")
st.divider()

init_fake_session()

# Render existing chat history
st.subheader("Chat History (render_chat_history)")
render_chat_history()

st.divider()

# Test the streaming function live
st.subheader("Streaming Response Test (render_streaming_response)")
st.caption("Click the button to simulate a live streamed response from the backend.")

if st.button("▶️ Simulate Streamed Response"):
    streamed_text = render_streaming_response(fake_stream())
    st.success(f"✅ Stream complete. Full text captured: `{streamed_text}`")