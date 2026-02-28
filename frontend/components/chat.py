"""
components/chat.py
------------------
Renders the full chat history from st.session_state.messages.

Message structure expected:
    {
        "role": "user" | "assistant",
        "content": "message text",
        "agent_logs": [                    # only on assistant messages, optional
            {
                "agent": "🩺 Pharmacist",
                "log": "agent result text"
            }
        ]
    }

Rules:
- Never modifies session_state
- UI only — no API calls, no logic
"""

import streamlit as st


# ── Agent colour map ──────────────────────────────────────────────────────────
AGENT_COLORS = {
    "🩺 Pharmacist":        "#7C3AED",   # purple
    "🛡️ Safety":            "#DC2626",   # red
    "📦 Fulfillment":       "#059669",   # green
}

DEFAULT_AGENT_COLOR = "#6B7280"          # grey fallback


def _agent_color(agent_name: str) -> str:
    """Return the hex colour for a given agent name."""
    for key, color in AGENT_COLORS.items():
        if key in agent_name:
            return color
    return DEFAULT_AGENT_COLOR


# ── Agent logs block ──────────────────────────────────────────────────────────
def _render_agent_logs(agent_logs: list) -> None:
    """
    Renders collapsed agent-thinking blocks beneath an assistant message.
    Each agent gets its own styled expander.
    """
    if not agent_logs:
        return

    st.markdown(
        "<p style='font-size:0.72rem; color:#6B7280; margin: 6px 0 4px 0;'>"
        "🤖 Agent reasoning</p>",
        unsafe_allow_html=True,
    )

    for entry in agent_logs:
        agent_name = entry.get("agent", "Agent")
        log_text   = entry.get("log", "No output.")
        color      = _agent_color(agent_name)

        # Styled expander label with coloured dot
        label = f"&nbsp; {agent_name}"
        dot_style = (
            f"display:inline-block; width:8px; height:8px; border-radius:50%; "
            f"background:{color}; margin-right:6px; vertical-align:middle;"
        )

        with st.expander(agent_name, expanded=False):
            st.markdown(
                f"""
                <div style="
                    background: #1a0a2e;
                    border-left: 3px solid {color};
                    border-radius: 6px;
                    padding: 12px 14px;
                    font-size: 0.82rem;
                    line-height: 1.6;
                    color: #e2e8f0;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                ">
                {log_text}
                </div>
                """,
                unsafe_allow_html=True,
            )


# ── Single message renderer ───────────────────────────────────────────────────
def _render_message(message: dict, index: int) -> None:
    """
    Renders one message bubble.
    - User messages: right-aligned purple bubble
    - Assistant messages: left-aligned dark bubble + agent logs below
    """
    role       = message.get("role", "user")
    content    = message.get("content", "")
    agent_logs = message.get("agent_logs", [])

    if role == "user":
     st.markdown(
        f"""
        <div style="
            display: flex;
            justify-content: flex-end;
            width: 100%;
            padding: 4px 0;
        ">
            <div style="
                background: linear-gradient(135deg, #7C3AED, #5B21B6);
                border-radius: 14px 14px 2px 14px;
                padding: 10px 16px;
                max-width: 75%;
                font-size: 0.92rem;
                line-height: 1.55;
                color: #ffffff;
                box-shadow: 0 2px 12px rgba(124,58,237,0.35);
                word-wrap: break-word;
            ">
            {content}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
         )

    elif role == "assistant":
        with st.chat_message("assistant"):
            # Main response text
            st.markdown(
                f"""
                <div style="
                    background: #1a0a2e;
                    border: 1px solid #2d1a4e;
                    border-radius: 14px 14px 14px 2px;
                    padding: 12px 16px;
                    max-width: 90%;
                    font-size: 0.92rem;
                    line-height: 1.6;
                    color: #f0f0f0;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
                ">
                {content}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Agent logs beneath the response (collapsed by default)
            if agent_logs:
                st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)
                _render_agent_logs(agent_logs)


# ── Main render function ──────────────────────────────────────────────────────
def render_chat_history() -> None:
    """
    Public entry point. Call this from app.py to render the full chat.

    Reads from:   st.session_state.messages
    Modifies:     nothing

    Usage in app.py:
        from components.chat import render_chat_history
        render_chat_history()
    """
    messages: list = st.session_state.get("messages", [])

    if not messages:
        # Fallback — should never hit this if session.py is set up correctly
        st.info("No messages yet. Start chatting below!")
        return

    for i, message in enumerate(messages):
        _render_message(message, index=i)


# ── Streaming assistant message ───────────────────────────────────────────────
def render_streaming_response(stream_generator) -> str:
    """
    Streams the final assistant response token by token into a chat bubble.
    Returns the full assembled string once streaming is complete.

    Usage in app.py (after agents finish):
        full_text = render_streaming_response(api_client.call_final_streamed(user_input))
    
    DEMO SAFETY: wrapped in try/except — if the stream breaks mid-way,
    whatever was collected so far is returned rather than crashing.
    """
    full_text = ""

    try:
        with st.chat_message("assistant"):
            placeholder = st.empty()

            for chunk in stream_generator:
                full_text += chunk
                placeholder.markdown(
                    f"""
                    <div style="
                        background: #1a0a2e;
                        border: 1px solid #2d1a4e;
                        border-radius: 14px 14px 14px 2px;
                        padding: 12px 16px;
                        max-width: 90%;
                        font-size: 0.92rem;
                        line-height: 1.6;
                        color: #f0f0f0;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.4);
                    ">
                    {full_text} ▌
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Final render — remove the cursor
            placeholder.markdown(
                f"""
                <div style="
                    background: #1a0a2e;
                    border: 1px solid #2d1a4e;
                    border-radius: 14px 14px 14px 2px;
                    padding: 12px 16px;
                    max-width: 90%;
                    font-size: 0.92rem;
                    line-height: 1.6;
                    color: #f0f0f0;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
                ">
                {full_text}
                </div>
                """,
                unsafe_allow_html=True,
            )

    except Exception as e:
        # ⚠️ DEMO SAFETY: stream broke — show what we have
        st.warning(f"Stream interrupted: {e}. Partial response captured.")

    return full_text