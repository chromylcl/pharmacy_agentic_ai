"""
components/quick_actions.py
----------------------------
Renders zero-state quick action suggestion buttons.
These appear ONLY when is_first_message == True (fresh session).
They vanish the moment the user sends their first message.

Rules:
    - Never modifies session_state directly
    - Returns the clicked prompt text so app.py can inject it into chat
    - No API calls
    - No agent logic

Usage in app.py:
    from components.quick_actions import render_quick_actions
    clicked = render_quick_actions()
    if clicked:
        # treat clicked as the user's first message
        handle_user_message(clicked)
"""

import streamlit as st

# 🔌 SWAP THIS — QUICK_ACTION_PROMPTS is currently imported from config.py (hardcoded list).
# When backend is ready and you want personalised suggestions based on patient history:
#   from services.api_client import get_suggested_prompts
#   prompts = get_suggested_prompts(st.session_state.patient_name)
# For now, pulling from config.py static list — no change needed until personalisation is added.
from config import QUICK_ACTION_PROMPTS


# ══════════════════════════════════════════════════════════════════════════════
# 🎨 LAYOUT CONFIG
# ══════════════════════════════════════════════════════════════════════════════

# How many buttons per row
COLUMNS = 2


# ══════════════════════════════════════════════════════════════════════════════
# 🚀 MAIN PUBLIC FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def render_quick_actions() -> str | None:
    """
    Renders suggestion buttons in a grid layout.
    Only shows when st.session_state.is_first_message is True.

    Returns:
        The prompt string if a button was clicked, otherwise None.
        app.py uses the returned string as the user's first message.

    Usage in app.py:
        clicked = render_quick_actions()
        if clicked:
            handle_user_message(clicked)
    """

    # Only show on fresh session
    if not st.session_state.get("is_first_message", True):
        return None

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="
            text-align: center;
            padding: 32px 0 20px 0;
        ">
            <div style="
                font-size: 2rem;
                margin-bottom: 10px;
            ">💊</div>
            <div style="
                font-size: 1.4rem;
                font-weight: 700;
                color: #ffffff;
                margin-bottom: 6px;
            ">How can Pharmacy Assistant help you today?</div>
            <div style="
                font-size: 0.85rem;
                color: #6B7280;
            ">Select a prompt below or type your own question</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Suggestion buttons grid ───────────────────────────────────────────────
    clicked_prompt = None
    prompts = QUICK_ACTION_PROMPTS

    # Split prompts into rows of COLUMNS
    rows = [prompts[i:i + COLUMNS] for i in range(0, len(prompts), COLUMNS)]

    for row in rows:
        cols = st.columns(COLUMNS)
        for col, prompt_tuple in zip(cols, row):
            with col:
                # FIX: Unpack the tuple into strings to prevent Streamlit TypeError
                emoji, label, full_prompt = prompt_tuple
                if st.button(
                    f"{emoji} {label}",
                    use_container_width=True,
                    key=f"quick_action_{label}",  # unique key per button using the label
                ):
                    clicked_prompt = full_prompt

    # ── Divider before chat input ─────────────────────────────────────────────
    if prompts:
        st.markdown(
            "<div style='margin-top: 24px;'></div>",
            unsafe_allow_html=True,
        )

    return clicked_prompt