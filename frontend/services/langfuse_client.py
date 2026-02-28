"""
services/langfuse_client.py
----------------------------
Handles all Langfuse observability — traces and spans.
One trace per user interaction. One span per agent call.

Rules:
    - No UI code
    - No session_state writes
    - Only called from agent_display.py and app.py

Usage:
    from services.langfuse_client import start_trace, log_span, end_trace

    trace = start_trace(user_input)
    log_span(trace, agent="🩺 Pharmacist", input=user_input, output=result)
    end_trace(trace)
"""

import os
import time
from dotenv import load_dotenv

load_dotenv()

# ══════════════════════════════════════════════════════════════════════════════
# 🔧 LANGFUSE INIT
# Created once at module level — do not re-create inside functions.
# ══════════════════════════════════════════════════════════════════════════════

# 🔌 SWAP THIS — if you move from Langfuse Cloud to a self-hosted instance,
# update LANGFUSE_HOST in your .env file to your self-hosted URL.
# Everything else stays the same.
from langfuse import Langfuse

_langfuse = Langfuse(
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key = os.getenv("LANGFUSE_SECRET_KEY"),
    host       = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
)


# ══════════════════════════════════════════════════════════════════════════════
# 🚀 PUBLIC FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def start_trace(user_input: str, patient_name: str = "Guest Patient"):
    """
    Starts a new Langfuse trace for one full user interaction.
    Call this once at the start of handling a user message.

    Args:
        user_input:   the raw message the user typed
        patient_name: from st.session_state.patient_name

    Returns:
        trace object — pass this into log_span() and end_trace()

    Usage in app.py:
        trace = start_trace(user_input, st.session_state.patient_name)
    """
    try:
        trace = _langfuse.trace(
            name     = "pharmacy-assistant-interaction",
            input    = user_input,
            metadata = {
                "patient": patient_name,
                "app":     "Atharva",
            },
        )
        return trace

    except Exception as e:
        # ⚠️ DEMO SAFETY: if Langfuse is unreachable, return a dummy trace
        # so the rest of the app doesn't crash. Observability fails silently.
        print(f"[Langfuse] start_trace failed: {e}")
        return _DummyTrace()


def log_span(
    trace,
    agent:   str,
    input:   str,
    output:  str,
    latency: float = 0.0,
):
    """
    Logs one agent call as a nested span inside the trace.
    Call this once per agent after it returns its result.

    Args:
        trace:   trace object returned by start_trace()
        agent:   agent label string e.g. "🩺 Pharmacist Agent"
        input:   what was sent to the agent (user message)
        output:  what the agent returned
        latency: time taken in seconds (use time.time() diff)

    Usage in agent_display.py:
        start_time = time.time()
        result = _call_pharmacist(user_input)
        latency = time.time() - start_time
        log_span(trace, "🩺 Pharmacist Agent", user_input, result, latency)
    """
    try:
        trace.span(
            name     = agent,
            input    = input,
            output   = output,
            metadata = {
                "agent":         agent,
                "latency_secs":  round(latency, 3),
            },
        )

    except Exception as e:
        # ⚠️ DEMO SAFETY: span logging fails silently — app keeps running
        print(f"[Langfuse] log_span failed for {agent}: {e}")


def end_trace(trace, final_response: str = ""):
    """
    Finalizes the trace with the assistant's final response and
    flushes everything to the Langfuse dashboard.
    Call this once after all agents and streaming are done.

    Args:
        trace:          trace object from start_trace()
        final_response: the full streamed text shown to the user

    Usage in app.py:
        end_trace(trace, full_response_text)
    """
    try:
        trace.update(output=final_response)
        _langfuse.flush()

    except Exception as e:
        # ⚠️ DEMO SAFETY: flush fails silently
        print(f"[Langfuse] end_trace failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# 🛡️ DUMMY TRACE — fallback if Langfuse is unreachable during demo
# ══════════════════════════════════════════════════════════════════════════════

class _DummyTrace:
    """
    Silent no-op trace used when Langfuse connection fails.
    Prevents the app from crashing if Langfuse is down during demo.
    All methods do nothing but won't raise errors.
    """
    def span(self, **kwargs):   pass
    def update(self, **kwargs): pass