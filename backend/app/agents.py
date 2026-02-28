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
        print("LLM OUTPUT:", data)
    except:
        return {"error": "Could not understand order"}
    intent = data.get("intent")

# 🔵 SYMPTOM INTENT
    if intent == "recommend":
        from .services import recommend_from_symptom  # we’ll create this next
        symptom = data["symptom"]

        recommendations = recommend_from_symptom(db, symptom)

        return {
        "message": f"Based on your symptom '{symptom}', I recommend:",
        "recommendations": recommendations,
        "trace": [
            "User message received",
            f"LLM extracted symptom: {symptom}",
            "Searching database for matching medicines"
        ]
    }
    # 🟢 ORDER INTENT
    elif intent == "order":
        
        medicine = data["medicine"]
        quantity = data["quantity"]
        dosage = data["dosage_frequency"]
        medicine = data["medicine"]
        quantity = data["quantity"]
        dosage = data["dosage_frequency"]
        

    # 🔴 OVERDOSE CHECK
    recent = check_recent_purchase(db, user_id, medicine)
    if recent:
        return {
            "warning": "You recently purchased this medicine. Please confirm if this is intentional."
        }

    



    # 🟢 STOCK CHECK
    stock_check = check_stock(db, medicine, quantity)
    if stock_check["status"] != "available":
        return stock_check

    # 🔴 PRESCRIPTION CHECK
    prescription = check_prescription(db, medicine)
    if prescription["prescription_required"]:
        return {"status": "prescription_required"}

    # 🟢 PLACE ORDER
    result = place_order(db, user_id, medicine, quantity, dosage)

    # 🔥 PROACTIVE REFILL SUGGESTION
    refill_alert = predict_refill(db, user_id)


    if isinstance(refill_alert, list) and len(refill_alert) > 0:
        result["proactive_suggestion"] = {
        "medicine": refill_alert[0]["medicine"],
        "expected_run_out": refill_alert[0]["expected_run_out"]
    }

    
        
    

    response_message = f"✅ Your order for {result['product']} has been placed successfully."

    if "proactive_suggestion" in result:
        response_message += f"\n\n⚠️ You may also run out of {result['proactive_suggestion']['medicine']} soon. Would you like to reorder?"


    trace = []
    trace.append("User message received")
    trace.append(f"LLM extracted: {data}")
    trace.append("Checking stock")
    trace.append("Checking prescription")
    trace.append("Placing order")

    return {
    "message": response_message,
    "data": result,
    "trace": trace
}


    







