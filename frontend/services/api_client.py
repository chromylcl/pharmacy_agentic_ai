"""
services/api_client.py
-----------------------
Every single HTTP call to the FastAPI backend lives here.
No UI code. No session_state. Just API calls.

When backend is ready:
    - Search for every "# 🔌 SWAP THIS" comment
    - Follow the exact instructions at each swap point
    - Test each function individually using test_api_client.py

Backend base URL: http://localhost:8000 (set in .env as BACKEND_URL)
"""

import os
import time
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth # ← Add this if it's missing

load_dotenv()

# 🔌 SWAP THIS — BACKEND_URL comes from .env file.
# When backend is deployed (not just localhost), update .env:
#   BACKEND_URL=https://your-deployed-backend.com
# No code change needed here — it reads from .env automatically.
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# How long to wait for backend before giving up (seconds)
# 🔌 SWAP THIS — increase timeout if your agents are slow on the real backend
TIMEOUT = 30


# ══════════════════════════════════════════════════════════════════════════════
# 🩺 PHARMACIST AGENT
# ══════════════════════════════════════════════════════════════════════════════

def call_pharmacist(text: str) -> str:
    """
    Calls the Pharmacist agent endpoint.

    Args:
        text: user's message

    Returns:
        Agent response as a string

    # 🔌 SWAP THIS — currently returns dummy data.
    # When backend is ready, uncomment the requests block below
    # and delete the dummy return line.
    #
    # Real backend call:
    #   response = requests.post(
    #       f"{BACKEND_URL}/agents/pharmacist",
    #       json={"message": text},
    #       timeout=TIMEOUT
    #   )
    #   response.raise_for_status()
    #   return response.json().get("result", "No response from pharmacist agent.")
    #
    # Expected backend request body:  { "message": "user text" }
    # Expected backend response body: { "result": "agent output string" }
    """
    # 🔌 SWAP THIS — delete these 2 lines and uncomment the block above
    time.sleep(1.2)
    return (
        "Assessment: Symptoms suggest a common cold or mild viral infection.\n"
        "Recommendation: Paracetamol 500mg every 4–6 hours for fever/pain relief.\n"
        "OTC availability: Yes — no prescription required.\n"
        "Follow-up: If symptoms persist beyond 5 days, consult a physician."
    )


# ══════════════════════════════════════════════════════════════════════════════
# 🛡️ SAFETY AGENT
# ══════════════════════════════════════════════════════════════════════════════

def call_safety(text: str) -> str:
    """
    Calls the Safety & Compliance agent endpoint.

    Args:
        text: user's message

    Returns:
        Agent response as a string

    # 🔌 SWAP THIS — currently returns dummy data.
    # When backend is ready, uncomment the requests block below
    # and delete the dummy return line.
    #
    # Real backend call:
    #   response = requests.post(
    #       f"{BACKEND_URL}/agents/safety",
    #       json={"message": text},
    #       timeout=TIMEOUT
    #   )
    #   response.raise_for_status()
    #   return response.json().get("result", "No response from safety agent.")
    #
    # Expected backend request body:  { "message": "user text" }
    # Expected backend response body: { "result": "agent output string" }
    """
    # 🔌 SWAP THIS — delete these 2 lines and uncomment the block above
    time.sleep(1.0)
    return (
        "Drug interaction scan: No active medications on file.\n"
        "Safety status: ✅ CLEAR — no contraindications detected.\n"
        "Dosage check: Within safe limits for standard adult dosage.\n"
        "Warnings: Avoid alcohol. Do not exceed 4g paracetamol/day."
    )


# ══════════════════════════════════════════════════════════════════════════════
# 📦 FULFILLMENT AGENT
# ══════════════════════════════════════════════════════════════════════════════

def call_fulfillment(text: str) -> str:
    """
    Calls the Fulfillment agent endpoint.

    Args:
        text: user's message

    Returns:
        Agent response as a string

    # 🔌 SWAP THIS — currently returns dummy data.
    # When backend is ready, uncomment the requests block below
    # and delete the dummy return line.
    #
    # Real backend call:
    #   response = requests.post(
    #       f"{BACKEND_URL}/agents/fulfillment",
    #       json={"message": text},
    #       timeout=TIMEOUT
    #   )
    #   response.raise_for_status()
    #   return response.json().get("result", "No response from fulfillment agent.")
    #
    # Expected backend request body:  { "message": "user text" }
    # Expected backend response body: { "result": "agent output string" }
    """
    # 🔌 SWAP THIS — delete these 2 lines and uncomment the block above
    time.sleep(0.8)
    return (
        "Inventory check: Paracetamol 500mg — IN STOCK ✅\n"
        "PDC Score: N/A (no refill history on file).\n"
        "Refill risk: LOW\n"
        "Estimated supply: 3-day course = 12 tablets available."
    )


# ══════════════════════════════════════════════════════════════════════════════
# 💬 FINAL STREAMED RESPONSE
# ══════════════════════════════════════════════════════════════════════════════

def call_final_streamed(text: str):
    """
    Calls the main /chat endpoint and streams the response token by token.
    This is the final answer shown to the user after all agents finish.

    Args:
        text: user's message

    Yields:
        string chunks (tokens) one at a time

    # 🔌 SWAP THIS — currently yields a fake token-by-token stream.
    # When backend is ready, uncomment the requests block below
    # and delete the dummy yield loop.
    #
    # Real backend call (streaming):
    #   with requests.post(
    #       f"{BACKEND_URL}/chat",
    #       json={"message": text},
    #       stream=True,
    #       timeout=TIMEOUT
    #   ) as response:
    #       response.raise_for_status()
    #       for chunk in response.iter_content(chunk_size=None):
    #           if chunk:
    #               yield chunk.decode("utf-8")
    #
    # Expected backend request body:  { "message": "user text" }
    # Expected backend response:      streaming text chunks (not JSON)
    # Backend must set: StreamingResponse with media_type="text/plain"
    """
    # 🔌 SWAP THIS — delete this entire dummy block and uncomment the real call above
    dummy_response = (
        f"Based on your query, here is my recommendation. "
        f"Please follow the dosage instructions carefully and consult "
        f"a healthcare professional if symptoms persist or worsen. "
        f"Stay hydrated and get adequate rest. 💊"
    )
    for word in dummy_response.split(" "):
        time.sleep(0.05)
        yield word + " "


# ══════════════════════════════════════════════════════════════════════════════
# 🎙️ VOICE TRANSCRIPTION
# ══════════════════════════════════════════════════════════════════════════════

def call_transcribe(audio_bytes: bytes) -> str:
    """
    Sends audio bytes to the backend for transcription.

    Args:
        audio_bytes: raw audio bytes from st.audio_input()

    Returns:
        Transcribed text string

    # 🔌 SWAP THIS — currently returns a dummy string.
    # When backend is ready, uncomment the requests block below
    # and delete the dummy return line.
    #
    # Real backend call:
    #   response = requests.post(
    #       f"{BACKEND_URL}/voice/transcribe",
    #       files={"audio": ("audio.wav", audio_bytes, "audio/wav")},
    #       timeout=TIMEOUT
    #   )
    #   response.raise_for_status()
    #   return response.json().get("text", "Could not transcribe audio.")
    #
    # Expected backend request: multipart/form-data with audio file
    # Expected backend response body: { "text": "transcribed string" }
    """
    # 🔌 SWAP THIS — delete this line and uncomment the block above
    return "I have a headache and mild fever. What can I take?"


# ══════════════════════════════════════════════════════════════════════════════
# 📊 REFILL CHECK
# ══════════════════════════════════════════════════════════════════════════════

def call_refill_check(patient_id: str, medication: str) -> dict:
    """
    Checks refill risk and PDC score for a patient's medication.

    Args:
        patient_id:  patient identifier
        medication:  medication name to check

    Returns:
        dict with keys: pdc_score (float), risk_level (str), days_remaining (int)

    # 🔌 SWAP THIS — currently returns dummy dict.
    # When backend is ready, uncomment the requests block below
    # and delete the dummy return line.
    #
    # Real backend call:
    #   response = requests.post(
    #       f"{BACKEND_URL}/refill/check",
    #       json={"patient_id": patient_id, "medication": medication},
    #       timeout=TIMEOUT
    #   )
    #   response.raise_for_status()
    #   return response.json()
    #
    # Expected backend request body:
    #   { "patient_id": "string", "medication": "string" }
    # Expected backend response body:
    #   { "pdc_score": 0.85, "risk_level": "LOW", "days_remaining": 12 }
    """
    # 🔌 SWAP THIS — delete this return and uncomment the block above
    return {
        "pdc_score":      0.85,
        "risk_level":     "LOW",
        "days_remaining": 12,
    }

def call_inventory() -> list:
    # This expects the backend to return: {"products": [ {name, price, stock, category, restricted}, ... ]}
    try:
        res = requests.get(f"{BACKEND_URL}/inventory", timeout=TIMEOUT)
        res.raise_for_status()
        return res.json().get("products", [])
    except Exception as e:
        # If backend is down, return empty list so the app doesn't crash during the demo
        return []
    

# ══════════════════════════════════════════════════════════════════════════════
# 💳 PAYPAL PAYMENT GATEWAY (SANDBOX)
# ══════════════════════════════════════════════════════════════════════════════

# ... (after call_inventory)

import requests
import requests.auth
import os

# Ensure these match your .env exactly
PP_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PP_SECRET = os.getenv("PAYPAL_SECRET")

def get_paypal_token():
    url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
    data = {"grant_type": "client_credentials"}
    try:
        # Use requests.auth.HTTPBasicAuth to fix the yellow line warning
        res = requests.post(
            url, 
            data=data, 
            auth=requests.auth.HTTPBasicAuth(PP_CLIENT_ID, PP_SECRET), 
            timeout=10
        )
        res.raise_for_status()
        return res.json().get("access_token")
    except Exception as e:
        print(f"PayPal Auth Error: {e}")
        return None

def call_create_payment_link(amount_usd: float, patient_name: str) -> str:
    token = get_paypal_token()
    if not token:
        return "https://www.paypal.com/checkoutnow"

    url = "https://api-m.sandbox.paypal.com/v2/checkout/orders"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # 🧪 FIX: PayPal requires amount as a string with exactly 2 decimal places
    formatted_amount = "{:.2f}".format(amount_usd)

    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD", 
                "value": formatted_amount
            }
        }],
        "application_context": {
            "brand_name": "AI Pharmacy Assistant",
            "return_url": "http://localhost:8501", 
            "cancel_url": "http://localhost:8501",
            "user_action": "PAY_NOW"
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        # If this fails, it will print the exact reason in your terminal
        if response.status_code != 201:
            print(f"PayPal Order Error: {response.text}")
            
        data = response.json()
        for link in data.get("links", []):
            if link["rel"] == "approve":
                return link["href"]
    except Exception as e:
        print(f"Request Exception: {e}")
    
    return "https://www.paypal.com/checkoutnow"
    

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        for link in data.get("links", []):
            if link["rel"] == "approve":
                return link["href"]
    except Exception as e:
        print(f"PayPal Order Error: {e}")
    
    return "https://www.paypal.com/checkoutnow"

# ══════════════════════════════════════════════════════════════════════════════
# 🛡️ ERROR HANDLER — wraps any api call safely
# ══════════════════════════════════════════════════════════════════════════════

def safe_call(func, *args, fallback="Agent unavailable. Please try again.", **kwargs):
    """
    Wraps any api_client function in a try/except.
    Use this in agent_display.py for extra demo safety.

    Usage:
        result = safe_call(call_pharmacist, user_input)
        result = safe_call(call_safety, user_input, fallback="Safety check failed.")

    ⚠️ DEMO SAFETY: if backend is down mid-demo, returns fallback string
    instead of crashing the entire app.
    """
    try:
        return func(*args, **kwargs)
    except requests.exceptions.ConnectionError:
        return f"⚠️ Backend unreachable. {fallback}"
    except requests.exceptions.Timeout:
        return f"⚠️ Backend timed out after {TIMEOUT}s. {fallback}"
    except requests.exceptions.HTTPError as e:
        return f"⚠️ Backend error {e.response.status_code}. {fallback}"
    except Exception as e:
        return f"⚠️ Unexpected error: {str(e)}. {fallback}"