"""
utils/drug_detector.py
-----------------------
Pure logic — no UI, no API calls, no session_state.
Detects restricted/prescription-only drug names in user input.

Usage in app.py:
    from utils.drug_detector import is_restricted_drug, get_detected_drug
    if is_restricted_drug(user_input):
        st.session_state.pending_prescription = get_detected_drug(user_input)
        st.session_state.ui_phase = "prescription_upload"
"""

# 🔌 SWAP THIS — RESTRICTED_DRUGS is currently a hardcoded list from config.py.
# When backend is ready with a live drug database:
#   from services.api_client import get_restricted_drug_list
#   RESTRICTED_DRUGS = get_restricted_drug_list()
# IMPORTANT: Cache this call — don't hit the endpoint on every message.
# Use @st.cache_data in api_client.py for this specific function.
# For now, static list from config.py is fine for the demo.
from config import RESTRICTED_DRUGS


def is_restricted_drug(text: str) -> bool:
    """
    Returns True if any restricted drug name is found in the user's message.
    Case-insensitive match.

    Args:
        text: raw user input string

    Returns:
        bool — True means block chat and show prescription upload screen

    Example:
        is_restricted_drug("I need some oxycodone")   → True
        is_restricted_drug("Can I take paracetamol")  → False
    """
    if not text:
        return False

    lowered = text.lower()
    return any(drug.lower() in lowered for drug in RESTRICTED_DRUGS)


def get_detected_drug(text: str) -> str | None:
    """
    Returns the first restricted drug name found in the text.
    Use this to set st.session_state.pending_prescription so
    prescription_upload.py knows which drug to display.

    Args:
        text: raw user input string

    Returns:
        The matched drug name string, or None if no match found

    Example:
        get_detected_drug("I need oxycodone 10mg")  → "oxycodone"
    """
    if not text:
        return None

    lowered = text.lower()
    for drug in RESTRICTED_DRUGS:
        if drug.lower() in lowered:
            return drug

    return None