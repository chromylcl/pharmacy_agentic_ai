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
from components.onboarding          import render_onboarding
from components.chat                import render_chat_history, render_streaming_response
from components.agent_display       import run_all_agents
from components.sidebar             import render_sidebar
from components.quick_actions       import render_quick_actions
from components.emergency_alert     import render_emergency_alert
from components.prescription_upload import render_prescription_upload
from components.receipt             import render_receipt
from styles.injector                import inject_global_css
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

# Hide Streamlit branding
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Make the main container slightly wider and more app-like */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)



# ══════════════════════════════════════════════════════════════════════════════
# 🔧 SESSION INIT
# ══════════════════════════════════════════════════════════════════════════════

init_session()
inject_global_css()

if st.session_state.ui_phase == "onboarding":
    render_onboarding()
    st.stop()



# 📐 SIDEBAR
render_sidebar()



# 🚨 EMERGENCY ROUTE
if st.session_state.ui_phase == "emergency_alert":
    render_emergency_alert(st.session_state.get("last_user_input", ""))
    st.stop()



# 📋 PRESCRIPTION UPLOAD ROUTE
if st.session_state.ui_phase == "prescription_upload":
    render_prescription_upload()
    st.stop()

# In app.py, add this right before your normal chat rendering starts
if st.session_state.ui_phase == "storefront":
    from components.storefront import render_storefront
    render_storefront()
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# 💬 NORMAL CHAT FLOW
# ══════════════════════════════════════════════════════════════════════════════

# ── 1. Render UI Components ──────────────────────────────────────────────────
clicked_prompt = render_quick_actions()
render_chat_history()
render_receipt()

# ── 2. Handle Inputs (Typed, Voice, Clicked, or Storefront Checkout) ─────────
voice_text = None
with st.expander("🎙️ Voice Input", expanded=False):
    audio = st.audio_input("Speak your question")
    if audio:
        with st.spinner("Transcribing..."):
            voice_text = safe_call(call_transcribe, audio.read())

user_input = st.chat_input("Ask about medications...")

# Separate what the user SEES from what the AI RECEIVES
display_input = None
llm_input = None

# Priority 1: Storefront Checkout Prompt
if st.session_state.get("checkout_prompt"):
    llm_input = st.session_state.checkout_prompt
    display_input = "🛒 *I would like to purchase the items in my cart. Please review for safety.*"
    # Clear the prompt immediately so it doesn't loop
    st.session_state.checkout_prompt = None

# Priority 2: Standard Inputs (Typed, Voice, or Quick Action)
else:
    active_input = user_input or voice_text or clicked_prompt
    if active_input:
        llm_input = active_input
        display_input = active_input

# ── 3. Processing Logic ──────────────────────────────────────────────────────
if llm_input and display_input:
    # Store for emergency context
    st.session_state.last_user_input = llm_input
    st.session_state.is_first_message = False

    # A. Emergency check
    if is_emergency(llm_input):
        st.session_state.ui_phase = "emergency_alert"
        st.rerun()

    # B. Restricted drug check
    if is_restricted_drug(llm_input):
        st.session_state.ui_phase = "prescription_upload"
        st.session_state.pending_prescription = get_detected_drug(llm_input)
        st.rerun()

    # C. Normal Agent Flow
    # 1. Append the FRIENDLY message to the UI
    st.session_state.messages.append({"role": "user", "content": display_input})
    
    # 2. Run everything else using the REAL hidden LLM prompt
    trace = start_trace(llm_input, st.session_state.patient_name)
    
    agent_logs = run_all_agents(llm_input)

    for entry in agent_logs:
        log_span(trace=trace, agent=entry["agent"], input=llm_input, output=entry["log"])

    full_response = render_streaming_response(call_final_streamed(llm_input))

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "agent_logs": agent_logs,
    })

    end_trace(trace, full_response)
    st.rerun()