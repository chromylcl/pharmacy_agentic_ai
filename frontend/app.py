"""
app.py
-------
Master entry point for AI Pharmacy Assistant.
Wires every component together following the decision flow:

    User message
        ↓
    is_emergency?       → YES → emergency_alert  → STOP
        ↓ NO
    is_restricted_drug? → YES → prescription_upload → STOP
        ↓ NO
    quick_actions (first message only)
        ↓
    run_all_agents → stream final response
        ↓
    append to messages → render receipt

Run with:
    streamlit run app.py
"""

import uuid
import streamlit as st

# ── Utils ─────────────────────────────────────────────────────────────────────
from utils.session          import init_session
from utils.emergency_detector import is_emergency
from utils.drug_detector    import is_restricted_drug, get_detected_drug

# ── Components ────────────────────────────────────────────────────────────────
from components.chat                import render_chat_history, render_streaming_response
from components.agent_display       import run_all_agents
from components.sidebar             import render_sidebar
from components.quick_actions       import render_quick_actions
from components.emergency_alert     import render_emergency_alert
from components.prescription_upload import render_prescription_upload
from components.receipt             import render_receipt

# ── Services ──────────────────────────────────────────────────────────────────
# 🔌 SWAP THIS — langfuse_client is fully wired in.
# If you want to disable tracing temporarily, comment out these 3 lines
# and replace trace = start_trace(...) calls below with trace = None
from services.langfuse_client import start_trace, log_span, end_trace

# 🔌 SWAP THIS — api_client is wired in with dummy data.
# When backend is ready, the functions inside api_client.py handle the swap.
# Nothing changes here in app.py — all swap points are inside api_client.py.
from services.api_client import call_final_streamed, call_transcribe, safe_call


# ══════════════════════════════════════════════════════════════════════════════
# ⚙️ PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title = "AI Pharmacy Assistant",
    page_icon  = "💊",
    layout     = "wide",
)


# ══════════════════════════════════════════════════════════════════════════════
# 🔧 SESSION INIT
# ══════════════════════════════════════════════════════════════════════════════

init_session()


# ══════════════════════════════════════════════════════════════════════════════
# 📐 SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

render_sidebar()


# ══════════════════════════════════════════════════════════════════════════════
# 🚨 EMERGENCY ROUTE — renders and stops if ui_phase = "emergency_alert"
# ══════════════════════════════════════════════════════════════════════════════

if st.session_state.ui_phase == "emergency_alert":
    render_emergency_alert(st.session_state.get("last_user_input", ""))
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# 📋 PRESCRIPTION UPLOAD ROUTE — renders and stops if ui_phase = "prescription_upload"
# ══════════════════════════════════════════════════════════════════════════════

if st.session_state.ui_phase == "prescription_upload":
    render_prescription_upload()
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# 💬 NORMAL CHAT FLOW
# ══════════════════════════════════════════════════════════════════════════════

# ── Quick actions (first message only) ───────────────────────────────────────
clicked_prompt = render_quick_actions()

# ── Chat history ─────────────────────────────────────────────────────────────
render_chat_history()

# ── Receipt (shows after first agent run) ────────────────────────────────────
render_receipt()

# ── Voice input ───────────────────────────────────────────────────────────────
# 🔌 SWAP THIS — st.audio_input is currently wired to call_transcribe().
# call_transcribe() returns dummy text until backend /voice/transcribe is ready.
# When backend is ready, swap inside services/api_client.py — nothing changes here.
voice_text = None
with st.expander("🎙️ Voice Input", expanded=False):
    audio = st.audio_input("Speak your question")
    if audio is not None:
        with st.spinner("Transcribing..."):
            voice_text = safe_call(call_transcribe, audio.read())
        if voice_text:
            st.success(f"Transcribed: *{voice_text}*")


# ══════════════════════════════════════════════════════════════════════════════
# ⌨️ CHAT INPUT — handles both typed and voice input
# ══════════════════════════════════════════════════════════════════════════════

# Pre-fill chat input from voice or quick action if available
prefill = voice_text or clicked_prompt or ""

user_input = st.chat_input(
    placeholder = "Ask about medications, symptoms, or drug interactions...",
)

# Use prefill if no typed input
if not user_input and prefill:
    user_input = prefill


# ══════════════════════════════════════════════════════════════════════════════
# 🧠 MESSAGE HANDLER
# ══════════════════════════════════════════════════════════════════════════════

if user_input:

    # Store for emergency alert display
    st.session_state.last_user_input = user_input

    # Mark first message as sent — hides quick actions
    st.session_state.is_first_message = False

    # ── Emergency check ───────────────────────────────────────────────────────
    if is_emergency(user_input):
        st.session_state.ui_phase = "emergency_alert"
        st.rerun()

    # ── Restricted drug check ─────────────────────────────────────────────────
    if is_restricted_drug(user_input):
        st.session_state.ui_phase            = "prescription_upload"
        st.session_state.pending_prescription = get_detected_drug(user_input)
        st.rerun()

    # ── Append user message to history ───────────────────────────────────────
    st.session_state.messages.append({
        "role":    "user",
        "content": user_input,
    })

    # ── Start Langfuse trace ──────────────────────────────────────────────────
    # 🔌 SWAP THIS — trace is real when langfuse keys are in .env.
    # If Langfuse is down, start_trace() returns a DummyTrace silently.
    trace = start_trace(user_input, st.session_state.patient_name)
    st.session_state.langfuse_trace_id = getattr(trace, "id", st.session_state.langfuse_trace_id)

    # ── Run all agents ────────────────────────────────────────────────────────
    # Returns list of {agent, log} dicts for attaching to the message
    # Also updates st.session_state.consultation_summary
    # 🔌 SWAP THIS — agent_display.py handles all swap points internally.
    # When backend is ready, swap inside components/agent_display.py.
    agent_logs = run_all_agents(user_input)

    # ── Log each agent span to Langfuse ──────────────────────────────────────
    for entry in agent_logs:
        log_span(
            trace  = trace,
            agent  = entry["agent"],
            input  = user_input,
            output = entry["log"],
        )

    # ── Stream final response ─────────────────────────────────────────────────
    # 🔌 SWAP THIS — call_final_streamed() uses dummy stream until backend ready.
    # When backend is ready, swap inside services/api_client.py.
    full_response = render_streaming_response(
        call_final_streamed(user_input)
    )

    # ── Append assistant message with agent logs ──────────────────────────────
    st.session_state.messages.append({
        "role":       "assistant",
        "content":    full_response,
        "agent_logs": agent_logs,
    })

    # ── End Langfuse trace ────────────────────────────────────────────────────
    end_trace(trace, full_response)

    # ── Rerun to refresh chat history cleanly ────────────────────────────────
    st.rerun()