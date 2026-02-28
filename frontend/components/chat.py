"""
components/chat.py
------------------
Renders the full chat history from st.session_state.messages.

Message structure expected:
    {
        "role": "user" | "assistant",
        "content": "message text",
        "agent_logs": [
            { "agent": "🩺 Pharmacist", "log": "agent result text" }
        ]
    }

Rules:
- Never modifies session_state
- UI only — no API calls, no logic
"""

import streamlit as st


AGENT_COLORS = {
    "🩺 Pharmacist":  "#7C3AED",
    "🛡️ Safety":      "#DC2626",
    "📦 Fulfillment": "#059669",
}
DEFAULT_AGENT_COLOR = "#6B7280"


def _inject_chat_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&display=swap');

        /* ── Global font ── */
        .stApp, .stChatMessage, [data-testid="stChatMessageContent"] {
            font-family: 'Sora', sans-serif !important;
        }

        /* ── Chat container background ── */
        .stApp {
            background:
                radial-gradient(ellipse at 15% 40%, rgba(59,7,100,0.4) 0%, transparent 55%),
                radial-gradient(ellipse at 85% 15%, rgba(30,27,75,0.3) 0%, transparent 55%),
                radial-gradient(ellipse at 50% 90%, rgba(12,10,26,0.8) 0%, transparent 60%),
                #06030f !important;
        }

        /* ── Native st.chat_message bubble — glass assistant ── */
        [data-testid="stChatMessage"] {
            background: rgba(255,255,255,0.03) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border: 1px solid rgba(124,58,237,0.15) !important;
            border-radius: 18px !important;
            padding: 0.8rem 1rem !important;
            margin-bottom: 0.5rem !important;
            box-shadow:
                0 4px 24px rgba(0,0,0,0.3),
                inset 0 1px 0 rgba(255,255,255,0.04) !important;
            transition: box-shadow 0.2s ease !important;
        }
        [data-testid="stChatMessage"]:hover {
            box-shadow:
                0 4px 32px rgba(124,58,237,0.15),
                inset 0 1px 0 rgba(255,255,255,0.06) !important;
        }

        /* ── Expander for agent logs — glass ── */
        [data-testid="stExpander"] {
            background: rgba(255,255,255,0.02) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(124,58,237,0.12) !important;
            border-radius: 12px !important;
            margin-top: 0.3rem !important;
        }
        [data-testid="stExpander"] summary {
            color: rgba(196,181,253,0.7) !important;
            font-size: 0.78rem !important;
            font-weight: 500 !important;
        }
        [data-testid="stExpander"] summary:hover {
            color: rgba(196,181,253,1) !important;
        }

        /* ── Chat input bar ── */
        [data-testid="stChatInput"] {
            background: rgba(255,255,255,0.04) !important;
            backdrop-filter: blur(20px) !important;
            border: 1px solid rgba(124,58,237,0.3) !important;
            border-radius: 16px !important;
            box-shadow: 0 0 30px rgba(124,58,237,0.08) !important;
        }
        [data-testid="stChatInput"] textarea {
            color: #f0e6ff !important;
            font-family: 'Sora', sans-serif !important;
            font-size: 0.9rem !important;
        }
        [data-testid="stChatInput"] textarea::placeholder {
            color: rgba(196,181,253,0.35) !important;
        }

        /* ── Scrollbar ── */
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(124,58,237,0.3); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(124,58,237,0.5); }

        @keyframes fadeInUp { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }
        @keyframes blink { 0%,100% { opacity:1; } 50% { opacity:0; } }
        </style>
    """, unsafe_allow_html=True)


def _agent_color(agent_name: str) -> str:
    for key, color in AGENT_COLORS.items():
        if key in agent_name:
            return color
    return DEFAULT_AGENT_COLOR


def _render_agent_logs(agent_logs: list) -> None:
    if not agent_logs:
        return

    st.markdown(
        "<p style='font-size:0.72rem; color:rgba(196,181,253,0.45); "
        "margin:8px 0 4px 2px; letter-spacing:0.04em; text-transform:uppercase;'>"
        "⚙ Agent Reasoning</p>",
        unsafe_allow_html=True,
    )

    for entry in agent_logs:
        agent_name = entry.get("agent", "Agent")
        log_text   = entry.get("log", "No output.")
        color      = _agent_color(agent_name)

        with st.expander(agent_name, expanded=False):
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, rgba(124,58,237,0.08), rgba(0,0,0,0.2));
                    border-left: 3px solid {color};
                    border-radius: 0 10px 10px 0;
                    padding: 12px 14px;
                    font-size: 0.82rem;
                    line-height: 1.7;
                    color: rgba(240,230,255,0.85);
                    white-space: pre-wrap;
                    word-wrap: break-word;
                    font-family: 'Sora', sans-serif;
                ">
                {log_text}
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_message(message: dict, index: int) -> None:
    role       = message.get("role", "user")
    content    = message.get("content", "")
    agent_logs = message.get("agent_logs", [])

    if role == "user":
        st.markdown(
            f"""
            <div style="
                display:flex; justify-content:flex-end;
                width:100%; padding:4px 0;
                animation: fadeInUp 0.3s ease;
            ">
                <div style="
                    background: linear-gradient(135deg, #7C3AED, #5B21B6);
                    border-radius: 18px 18px 4px 18px;
                    padding: 11px 18px;
                    max-width: 72%;
                    font-size: 0.9rem;
                    line-height: 1.6;
                    color: #fff;
                    box-shadow: 0 4px 20px rgba(124,58,237,0.4), inset 0 1px 0 rgba(255,255,255,0.15);
                    word-wrap: break-word;
                    font-family: 'Sora', sans-serif;
                    border: 1px solid rgba(167,139,250,0.3);
                ">
                {content}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    elif role == "assistant":
        with st.chat_message("assistant"):
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(124,58,237,0.05));
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(124,58,237,0.2);
                    border-radius: 4px 18px 18px 18px;
                    padding: 13px 17px;
                    max-width: 92%;
                    font-size: 0.9rem;
                    line-height: 1.7;
                    color: rgba(240,230,255,0.92);
                    box-shadow: 0 2px 16px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04);
                    word-wrap: break-word;
                    font-family: 'Sora', sans-serif;
                    animation: fadeInUp 0.3s ease;
                ">
                {content}
                </div>
                """,
                unsafe_allow_html=True,
            )
            if agent_logs:
                st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)
                _render_agent_logs(agent_logs)


def render_chat_history() -> None:
    """
    Public entry point. Call from app.py to render full chat.
    Reads from st.session_state.messages — never modifies it.
    """
    _inject_chat_css()

    messages: list = st.session_state.get("messages", [])

    if not messages:
        st.info("No messages yet. Start chatting below!")
        return

    for i, message in enumerate(messages):
        _render_message(message, index=i)


def render_streaming_response(stream_generator) -> str:
    """
    Streams final assistant response token by token into a glass chat bubble.
    Returns the full assembled string when streaming is complete.
    Wrapped in try/except — partial response captured if stream breaks mid-way.
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
                        background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(124,58,237,0.05));
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(124,58,237,0.2);
                        border-radius: 4px 18px 18px 18px;
                        padding: 13px 17px;
                        max-width: 92%;
                        font-size: 0.9rem;
                        line-height: 1.7;
                        color: rgba(240,230,255,0.92);
                        box-shadow: 0 2px 16px rgba(0,0,0,0.3);
                        word-wrap: break-word;
                        font-family: 'Sora', sans-serif;
                    ">
                    {full_text}<span style="
                        display:inline-block; width:2px; height:1em;
                        background:#7C3AED; margin-left:2px;
                        vertical-align:text-bottom;
                        animation: blink 1s step-end infinite;
                        border-radius:1px;
                    "></span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Final render — remove cursor
            placeholder.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(124,58,237,0.05));
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(124,58,237,0.2);
                    border-radius: 4px 18px 18px 18px;
                    padding: 13px 17px;
                    max-width: 92%;
                    font-size: 0.9rem;
                    line-height: 1.7;
                    color: rgba(240,230,255,0.92);
                    box-shadow: 0 2px 16px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04);
                    word-wrap: break-word;
                    font-family: 'Sora', sans-serif;
                ">
                {full_text}
                </div>
                """,
                unsafe_allow_html=True,
            )

    except Exception as e:
        st.warning(f"Stream interrupted: {e}. Partial response captured.")

    return full_text