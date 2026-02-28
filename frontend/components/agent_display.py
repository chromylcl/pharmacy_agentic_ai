"""
components/agent_display.py
----------------------------
Renders Grok-style st.status blocks for each agent.
Shows live "thinking" state then collapses cleanly once done.

Modifies session_state:
    - st.session_state.consultation_summary  (appends agent findings)
    - st.session_state.pending_prescription  (set if restricted drug found)

When backend is ready:
    - Search for "# 🔌 SWAP THIS" comments — those are the only lines to change
    - Replace dummy_* calls with real api_client calls
"""

import time
import streamlit as st


# ══════════════════════════════════════════════════════════════════════════════
# 🔧 DUMMY RESPONSES — Replace these when backend is ready
# ══════════════════════════════════════════════════════════════════════════════

def _dummy_pharmacist(user_input: str) -> str:
    time.sleep(1.2)   # Simulate network delay
    return (
        f"Analyzing query: '{user_input}'\n\n"
        "Assessment: Symptoms suggest a common cold or mild viral infection.\n"
        "Recommendation: Paracetamol 500mg every 4–6 hours for fever/pain relief.\n"
        "OTC availability: Yes — no prescription required.\n"
        "Follow-up: If symptoms persist beyond 5 days, consult a physician."
    )

def _dummy_safety(user_input: str) -> str:
    time.sleep(1.0)
    return (
        "Drug interaction scan: No active medications on file.\n"
        "Safety status: ✅ CLEAR — no contraindications detected.\n"
        "Dosage check: Within safe limits for standard adult dosage.\n"
        "Warnings: Avoid alcohol. Do not exceed 4g paracetamol/day."
    )

def _dummy_fulfillment(user_input: str) -> str:
    time.sleep(0.8)
    return (
        "Inventory check: Paracetamol 500mg — IN STOCK ✅\n"
        "PDC Score: N/A (no refill history on file).\n"
        "Refill risk: LOW\n"
        "Estimated supply: 3-day course = 12 tablets available."
    )

# ══════════════════════════════════════════════════════════════════════════════
# 🔌 API CALL WRAPPERS — Swap dummy_* with real calls here ONLY
# ══════════════════════════════════════════════════════════════════════════════

def _call_pharmacist(user_input: str) -> str:
    return _dummy_pharmacist(user_input)
    # 🔌 SWAP THIS — when backend is ready, replace above line with:
    # from services.api_client import call_pharmacist
    # return call_pharmacist(user_input)

def _call_safety(user_input: str) -> str:
    return _dummy_safety(user_input)
    # 🔌 SWAP THIS — when backend is ready, replace above line with:
    # from services.api_client import call_safety
    # return call_safety(user_input)

def _call_fulfillment(user_input: str) -> str:
    return _dummy_fulfillment(user_input)
    # 🔌 SWAP THIS — when backend is ready, replace above line with:
    # from services.api_client import call_fulfillment
    # return call_fulfillment(user_input)


# ══════════════════════════════════════════════════════════════════════════════
# 🎨 AGENT CONFIG — colours, icons, labels
# ══════════════════════════════════════════════════════════════════════════════

AGENTS = [
    {
        "key":   "pharmacist",
        "label": "🩺 Pharmacist Agent",
        "thinking_msg": "Analyzing symptoms and medications...",
        "color": "#7C3AED",
        "call":  _call_pharmacist,
    },
    {
        "key":   "safety",
        "label": "🛡️ Safety & Compliance Agent",
        "thinking_msg": "Scanning for drug interactions and dosage risks...",
        "color": "#DC2626",
        "call":  _call_safety,
    },
    {
        "key":   "fulfillment",
        "label": "📦 Fulfillment Agent",
        "thinking_msg": "Checking inventory and calculating PDC score...",
        "color": "#059669",
        "call":  _call_fulfillment,
    },
]


# ══════════════════════════════════════════════════════════════════════════════
# 🧠 SINGLE AGENT RUNNER
# ══════════════════════════════════════════════════════════════════════════════

def _run_agent(agent: dict, user_input: str) -> str:
    """
    Runs one agent inside a st.status block.
    Shows thinking state → runs call → collapses with result.
    Returns the agent's output string.
    """
    result = ""

    with st.status(agent["label"], expanded=True) as status:

        # Thinking state
        st.markdown(
            f"""
            <div style="
                font-size: 0.82rem;
                color: #94a3b8;
                padding: 4px 0;
            ">
                ⏳ {agent["thinking_msg"]}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Run the actual call (dummy or real)
        try:
            result = agent["call"](user_input)
        except Exception as e:
            result = f"⚠️ Agent failed: {str(e)}"
            status.update(
                label=f"{agent['label']} — Error",
                state="error",
                expanded=False,
            )
            return result

        # Show result inside the status block
        st.markdown(
            f"""
            <div style="
                background: #0a0a1a;
                border-left: 3px solid {agent['color']};
                border-radius: 6px;
                padding: 10px 14px;
                margin-top: 8px;
                font-size: 0.82rem;
                line-height: 1.65;
                color: #e2e8f0;
                white-space: pre-wrap;
                word-wrap: break-word;
            ">
{result}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Collapse cleanly once done
        status.update(
            label=f"{agent['label']} ✓",
            state="complete",
            expanded=False,
        )

    return result


# ══════════════════════════════════════════════════════════════════════════════
# 🚀 MAIN PUBLIC FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def run_all_agents(user_input: str) -> list:
    """
    Public entry point. Call this from app.py after emergency/drug checks pass.

    Runs all 3 agents sequentially with live st.status blocks.
    Updates st.session_state.consultation_summary with findings.

    Returns:
        agent_logs — list of {agent, log} dicts (for attaching to messages)

    Usage in app.py:
        from components.agent_display import run_all_agents
        agent_logs = run_all_agents(user_input)
    """
    agent_logs = []

    st.markdown(
        "<p style='font-size:0.78rem; color:#6B7280; margin-bottom:6px;'>"
        "🤖 Running agents...</p>",
        unsafe_allow_html=True,
    )

    for agent in AGENTS:
        result = _run_agent(agent, user_input)

        # Build log entry for chat history
        log_entry = {
            "agent": agent["label"],
            "log":   result,
        }
        agent_logs.append(log_entry)

        # Update consultation summary for receipt/PDF later
        timestamp = time.strftime("%H:%M:%S")
        st.session_state.consultation_summary.append({
            "agent":     agent["label"],
            "finding":   result,
            "timestamp": timestamp,
        })

    return agent_logs