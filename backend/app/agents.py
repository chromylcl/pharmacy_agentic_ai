import os
import json
from dotenv import load_dotenv
from groq import Groq
from sqlalchemy.orm import Session

from .services import (
    check_stock,
    check_prescription,
    place_order,
    check_recent_purchase,
    predict_refill
)
load_dotenv()

# ✅ THIS MUST EXIST
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are an AI Pharmacist.

If the user describes symptoms (like dry skin, tiredness, allergy, bladder issues, etc.)
respond with:

{
  "intent": "recommend",
  "symptom": "..."
}

If the user wants to order medicine, respond with:

{
  "intent": "order",
  "medicine": "...",
  "quantity": number,
  "dosage_frequency": number
}

Respond ONLY in JSON.
"""
def run_agent(db: Session, user_id: str, message: str):

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ],
        temperature=0
    )

    try:
        data = json.loads(completion.choices[0].message.content)
    except:
        return {"error": "Could not understand request"}

    intent = data.get("intent")

    # 🔵 SYMPTOM INTENT
    if intent == "recommend":
        from .services import recommend_from_symptom
        symptom = data.get("symptom")

        recommendations = recommend_from_symptom(db, symptom)

        return {
            "message": f"Based on your symptom '{symptom}', I recommend:",
            "recommendations": recommendations,
            "trace": ["Symptom detected", "Fetching recommendations"]
        }

    # 🟢 ORDER INTENT (VALIDATION PHASE ONLY)
    elif intent == "order":

        medicine = data.get("medicine")
        quantity = data.get("quantity", 1)
        dosage = data.get("dosage_frequency", 1)

        if not medicine:
            return {"error": "Medicine not detected"}

        # STOCK CHECK
        stock_check = check_stock(db, medicine, quantity)
        if stock_check["status"] != "available":
            return {
                "message": "❌ Medicine out of stock.",
                "status": "out_of_stock"
            }

        # PRESCRIPTION CHECK
        prescription = check_prescription(db, medicine)
        if prescription["prescription_required"]:
            return {
                "message": f"⚠️ {medicine} requires a prescription.",
                "status": "prescription_required"
            }

        # RETURN READY TO CONFIRM (DO NOT PLACE ORDER)
        return {
            "message": (
                f"✅ {medicine} is available.\n\n"
                f"Quantity: {quantity}\n"
                f"No prescription required.\n\n"
                f"Click Confirm to place your order."
            ),
            "status": "ready_to_confirm",
            "order_data": {
                "medicine": medicine,
                "quantity": quantity,
                "dosage": dosage
            }
        }

    return {"error": "Unknown intent"}