"""
components/emergency_alert.py
------------------------------
Renders the Red Route emergency bypass screen.
This replaces the entire chat UI when is_emergency() returns True.
No LLM is called. No agents run. This is hardcoded for safety.

Rules:
    - No API calls — this must work even if backend is completely down
    - No session_state writes
    - UI only

Usage in app.py:
    from components.emergency_alert import render_emergency_alert
    if st.session_state.ui_phase == "emergency_alert":
        render_emergency_alert(user_input)
        st.stop()
"""

import streamlit as st


# ══════════════════════════════════════════════════════════════════════════════
# 🚨 EMERGENCY CONTACTS
# These are hardcoded intentionally — never depend on backend for emergency info.
# ══════════════════════════════════════════════════════════════════════════════

# 🔌 SWAP THIS — numbers below are India defaults.
# Update these to match your target region before demo:
#   EMERGENCY_NUMBER   = "911"    # US
#   EMERGENCY_NUMBER   = "999"    # UK
#   EMERGENCY_NUMBER   = "112"    # EU / India (works across India too)
# No backend swap needed — keep these hardcoded always.
EMERGENCY_NUMBER    = "112"
POISON_CONTROL      = "1800-116-117"    # India Poison Control (toll-free)
AMBULANCE           = "108"             # India national ambulance


# ══════════════════════════════════════════════════════════════════════════════
# 🚀 MAIN PUBLIC FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def render_emergency_alert(user_input: str = "") -> None:
    """
    Renders a full-screen emergency alert with contact numbers.
    Call st.stop() immediately after this in app.py to prevent
    any further code from running.

    Args:
        user_input: the message that triggered the emergency (shown back to user)

    Usage in app.py:
        render_emergency_alert(user_input)
        st.stop()
    """

    # ── Red alert banner ──────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #7f1d1d, #DC2626);
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 4px 24px rgba(220,38,38,0.4);
        ">
            <div style="font-size: 3rem;">🚨</div>
            <div style="
                font-size: 1.5rem;
                font-weight: 800;
                color: #ffffff;
                margin: 8px 0 4px 0;
                letter-spacing: 0.02em;
            ">Emergency Detected</div>
            <div style="
                font-size: 0.9rem;
                color: #fca5a5;
            ">Please seek immediate medical attention</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── What triggered it ─────────────────────────────────────────────────────
    if user_input:
        st.markdown(
            f"""
            <div style="
                background: #1a0a0a;
                border: 1px solid #7f1d1d;
                border-radius: 8px;
                padding: 12px 16px;
                margin-bottom: 16px;
                font-size: 0.85rem;
                color: #fca5a5;
            ">
                ⚠️ &nbsp; Your message: <em>"{user_input}"</em>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Emergency contact cards ───────────────────────────────────────────────
    st.markdown(
        "<p style='font-size:0.78rem; color:#6B7280; margin-bottom:8px;'>"
        "CALL IMMEDIATELY</p>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div style="
                background: #1a0a0a;
                border: 2px solid #DC2626;
                border-radius: 10px;
                padding: 16px;
                text-align: center;
            ">
                <div style="font-size: 1.6rem;">🚑</div>
                <div style="color:#fca5a5; font-size:0.75rem; margin:4px 0;">AMBULANCE</div>
                <div style="color:#ffffff; font-size:1.4rem; font-weight:800;">{AMBULANCE}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div style="
                background: #1a0a0a;
                border: 2px solid #DC2626;
                border-radius: 10px;
                padding: 16px;
                text-align: center;
            ">
                <div style="font-size: 1.6rem;">🆘</div>
                <div style="color:#fca5a5; font-size:0.75rem; margin:4px 0;">EMERGENCY</div>
                <div style="color:#ffffff; font-size:1.4rem; font-weight:800;">{EMERGENCY_NUMBER}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div style="
                background: #1a0a0a;
                border: 2px solid #DC2626;
                border-radius: 10px;
                padding: 16px;
                text-align: center;
            ">
                <div style="font-size: 1.6rem;">☠️</div>
                <div style="color:#fca5a5; font-size:0.75rem; margin:4px 0;">POISON CONTROL</div>
                <div style="color:#ffffff; font-size:1.1rem; font-weight:800;">{POISON_CONTROL}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Instructions ─────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="
            background: #1a0a2e;
            border-left: 4px solid #DC2626;
            border-radius: 0 8px 8px 0;
            padding: 14px 18px;
            font-size: 0.85rem;
            line-height: 1.8;
            color: #e2e8f0;
        ">
            <strong style="color:#fca5a5;">While waiting for help:</strong><br>
            • Stay calm and stay on the line with emergency services<br>
            • Do not take any additional medications<br>
            • If unconscious, place in recovery position<br>
            • Unlock your door so responders can enter
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Reset button ──────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
    if st.button("← I'm safe, return to chat", use_container_width=False):
        st.session_state.ui_phase = "chatting"
        st.rerun()