"""
components/sidebar.py
----------------------
Renders the left sidebar with:
    
    - Patient name input
    - Session info (trace ID, message count)
    - Agent legend
    - Session reset button

Rules:
    - Only modifies st.session_state.patient_name
    - No API calls
    - No agent logic
"""

import streamlit as st


# ══════════════════════════════════════════════════════════════════════════════
# 🎨 BRANDING
# ══════════════════════════════════════════════════════════════════════════════

def _render_branding():
    st.markdown(
        """
        <div style="
            text-align: center;
            padding: 10px 0 20px 0;
        ">
            <div style="
                font-size: 2.2rem;
                margin-bottom: 4px;
            ">💊</div>
            <div style="
                font-size: 1.3rem;
                font-weight: 700;
                color: #ffffff;
                letter-spacing: 0.04em;
            ">AI Pharmacy</div>
            <div style="
                font-size: 0.72rem;
                color: #6B7280;
                margin-top: 2px;
            ">AI Pharmacy Assistant</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# 👤 PATIENT INFO
# ══════════════════════════════════════════════════════════════════════════════

def _render_patient_info():
    st.markdown(
        "<p style='font-size:0.75rem; color:#6B7280; margin-bottom:4px;'>"
        "PATIENT</p>",
        unsafe_allow_html=True,
    )

    # 🔌 SWAP THIS — Right now patient name is just a free text input.
    # When auth is ready, replace this text_input with a login widget
    # and pull the real patient name from your backend like:
    #   from services.api_client import get_patient_profile
    #   profile = get_patient_profile(patient_id)
    #   st.session_state.patient_name = profile["name"]
    name = st.text_input(
        label="Patient name",
        value=st.session_state.get("patient_name", "Guest Patient"),
        label_visibility="collapsed",
        placeholder="Enter your name...",
        key="patient_name_input",
    )

    # Update session state when name changes
    if name:
        st.session_state.patient_name = name

    # Patient badge
    st.markdown(
        f"""
        <div style="
            background: #1a0a2e;
            border: 1px solid #2d1a4e;
            border-radius: 8px;
            padding: 8px 12px;
            margin-top: 6px;
            font-size: 0.82rem;
            color: #e2e8f0;
        ">
            👤 &nbsp; {st.session_state.get("patient_name", "Guest Patient")}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# 📊 SESSION INFO
# ══════════════════════════════════════════════════════════════════════════════

def _render_session_info():
    st.markdown(
        "<p style='font-size:0.75rem; color:#6B7280; margin: 18px 0 6px 0;'>"
        "SESSION</p>",
        unsafe_allow_html=True,
    )

    messages     = st.session_state.get("messages", [])
    msg_count    = max(0, len(messages) - 1)   # subtract greeting

    # 🔌 SWAP THIS — trace_id is currently a local UUID generated in session.py.
    # When Langfuse is fully wired, the real trace ID comes from:
    #   from services.langfuse_client import start_trace
    #   trace = start_trace(user_input)
    #   st.session_state.langfuse_trace_id = trace.id
    # Nothing else changes here — the display picks it up automatically.
    trace_id     = st.session_state.get("langfuse_trace_id", "not set")
    short_trace  = trace_id[:8] + "..." if len(trace_id) > 8 else trace_id

    st.markdown(
        f"""
        <div style="
            background: #1a0a2e;
            border: 1px solid #2d1a4e;
            border-radius: 8px;
            padding: 10px 12px;
            font-size: 0.8rem;
            line-height: 2;
            color: #94a3b8;
        ">
            💬 &nbsp; <span style="color:#e2e8f0;">{msg_count}</span> messages<br>
            🔍 &nbsp; Trace: <span style="color:#7C3AED; font-family:monospace;">{short_trace}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )




# ══════════════════════════════════════════════════════════════════════════════
# 🤖 AGENT LEGEND
# ══════════════════════════════════════════════════════════════════════════════

def _render_agent_legend():
    st.markdown(
        "<p style='font-size:0.75rem; color:#6B7280; margin: 18px 0 6px 0;'>"
        "AGENTS</p>",
        unsafe_allow_html=True,
    )

    agents = [
        ("🩺", "Pharmacist",  "#7C3AED", "Symptoms & medication"),
        ("🛡️", "Safety",      "#DC2626", "Drug interactions"),
        ("📦", "Fulfillment", "#059669", "Inventory & PDC"),
    ]

    for icon, name, color, desc in agents:
        st.markdown(
            f"""
            <div style="
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 7px 10px;
                margin-bottom: 5px;
                background: #1a0a2e;
                border-left: 3px solid {color};
                border-radius: 0 6px 6px 0;
                font-size: 0.8rem;
            ">
                <span>{icon}</span>
                <div>
                    <div style="color:#e2e8f0; font-weight:600;">{name}</div>
                    <div style="color:#6B7280; font-size:0.72rem;">{desc}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )




# ══════════════════════════════════════════════════════════════════════════════
# 🛒 STOREFRONT
# ══════════════════════════════════════════════════════════════════════════════

def _render_storefront_button():
    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
    
    if st.button("🛒 Open Storefront", use_container_width=True, type="primary"):
        st.session_state.ui_phase = "storefront"
        st.rerun()



# ══════════════════════════════════════════════════════════════════════════════
# 🔄 RESET BUTTON
# ══════════════════════════════════════════════════════════════════════════════

def _render_reset_button():
    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

    if st.button("🔄 New Session", use_container_width=True):
        # Clear everything except patient name
        patient_name = st.session_state.get("patient_name", "Guest Patient")

        for key in list(st.session_state.keys()):
            del st.session_state[key]

        # 🔌 SWAP THIS — replace the manual re-init below with:
        #   from utils.session import init_session
        #   init_session()
        #   st.session_state.patient_name = patient_name
        # For now, manually restore essentials:
        import uuid
        st.session_state.patient_name          = patient_name
        st.session_state.ui_phase              = "chatting"
        st.session_state.is_first_message      = True
        st.session_state.messages              = [
            {
                "role":    "assistant",
                "content": "👋 Hello! I'm AI Pharmacy Assistant, your AI pharmacy assistant. How can I help you today?",
            }
        ]
        st.session_state.pending_prescription  = None
        st.session_state.langfuse_trace_id     = str(uuid.uuid4())
        st.session_state.consultation_summary  = []

        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# 🚀 MAIN PUBLIC FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def render_sidebar():
    """
    Public entry point. Call this from app.py inside a st.sidebar block.

    Usage in app.py:
        from components.sidebar import render_sidebar
        with st.sidebar:
            render_sidebar()
    """
    with st.sidebar:
        _render_branding()
        st.divider()
        _render_patient_info()
        _render_session_info()
        st.divider()
        _render_agent_legend()
        
        # ADDED: Storefront button right below the agents legend
        _render_storefront_button()
        
        st.divider()
        _render_reset_button()

        # Footer
        st.markdown(
            "<div style='position:fixed; bottom:16px; font-size:0.68rem; color:#374151;'>"
            "Built for Hackathon 2026 ⚡</div>",
            unsafe_allow_html=True,
        )