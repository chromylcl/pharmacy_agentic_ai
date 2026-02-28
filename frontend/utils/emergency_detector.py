"""
utils/emergency_detector.py
----------------------------
Pure logic — no UI, no API calls, no session_state.
Detects emergency phrases in user input.

Usage in app.py:
    from utils.emergency_detector import is_emergency
    if is_emergency(user_input):
        st.session_state.ui_phase = "emergency_alert"
"""

# 🔌 SWAP THIS — EMERGENCY_KEYWORDS is currently a hardcoded list from config.py.
# If backend ever exposes a dynamic keyword list endpoint:
#   from services.api_client import get_emergency_keywords
#   LIVE_KEYWORDS = get_emergency_keywords()
# For now this is intentionally hardcoded — emergency detection should
# NEVER depend on a network call (if backend is down, detection must still work).
from config import EMERGENCY_KEYWORDS


def is_emergency(text: str) -> bool:
    """
    Returns True if any emergency keyword is found in the user's message.
    Case-insensitive. Checks for whole phrase matches.

    Args:
        text: raw user input string

    Returns:
        bool — True means skip LLM entirely and show emergency alert

    Example:
        is_emergency("I think I'm having a heart attack")  → True
        is_emergency("I have a mild headache")             → False
    """
    if not text:
        return False

    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in EMERGENCY_KEYWORDS)