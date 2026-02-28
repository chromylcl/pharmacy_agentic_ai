from .intent_agent import detect_intent
from .safety_agent import run_safety_checks
from .inventory_agent import check_inventory
from .action_agent import execute_order

from ..services import recommend_from_symptom, fuzzy_match_medicine
from ..models import PendingOrder

def run_pharmacy_agent(db, user_id, message):

    trace = []

    # =====================================
    # 🚨 1️⃣ EMERGENCY DETECTION
    # =====================================
    RED_FLAGS = [
        "chest pain",
        "breathing difficulty",
        "can't breathe",
        "severe bleeding",
        "unconscious",
        "heart attack",
        "stroke"
    ]

    if any(flag in message.lower() for flag in RED_FLAGS):
        return {
            "message": "🚨 This sounds like a medical emergency. Please go to the nearest hospital immediately.",
            "trace": ["Emergency mode triggered"]
        }

    # =====================================
    # 🔁 2️⃣ CONTINUE PENDING ORDER (MULTI-TURN)
    # =====================================
    pending = db.query(PendingOrder).filter(
        PendingOrder.patient_id == user_id
    ).first()

    if pending and message.strip().isdigit():

        quantity = int(message.strip())
        medicine_input = pending.medicine_name

        trace.append("Continuing pending order")

        # Delete pending state
        db.delete(pending)
        db.commit()

        data = {
            "intent": "order",
            "medicine": medicine_input,
            "quantity": quantity,
            "dosage_frequency": 1
        }

    else:
        # =====================================
        # 🤖 3️⃣ INTENT DETECTION
        # =====================================
        data = detect_intent(message)
        trace.append(f"Intent detected: {data}")

    # =====================================
    # 🩺 4️⃣ RECOMMEND FLOW
    # =====================================
    if data.get("intent") == "recommend":

        symptom = data.get("symptom")

        if not symptom:
            return {
                "message": "Please describe your symptom clearly.",
                "trace": trace
            }

        recommendations = recommend_from_symptom(db, symptom)

        return {
            "message": f"Based on your symptom '{symptom}', I recommend:",
            "recommendations": recommendations,
            "trace": trace
        }

    # =====================================
    # 💊 5️⃣ ORDER FLOW
    # =====================================
    elif data.get("intent") == "order":

        medicine_input = data.get("medicine")
        quantity = data.get("quantity")
        dosage = data.get("dosage_frequency")

        trace.append("Order request received")

        # ❓ QUANTITY CLARIFICATION
        if not quantity:

            # Remove existing pending
            existing = db.query(PendingOrder).filter(
                PendingOrder.patient_id == user_id
            ).first()

            if existing:
                db.delete(existing)
                db.commit()

            pending = PendingOrder(
                patient_id=user_id,
                medicine_name=medicine_input
            )

            db.add(pending)
            db.commit()

            return {
                "message": f"How many units of {medicine_input} would you like?",
                "trace": ["Pending order saved"]
            }

        # 🔍 FUZZY MATCH
        medicine = fuzzy_match_medicine(db, medicine_input)

        if not medicine:
            return {
                "message": "Medicine not found. Please check spelling.",
                "trace": ["Fuzzy match failed"]
            }

        trace.append(f"Fuzzy matched medicine: {medicine}")

        # 📦 1️⃣ STOCK CHECK
        inventory = check_inventory(db, medicine, quantity)
        trace.append(f"Stock check: {inventory}")

        if inventory["status"] != "available":
            return {
                "message": "Medicine out of stock or insufficient quantity.",
                "trace": trace
            }

        # 🛡️ 2️⃣ SAFETY CHECK (Prescription + Overdose)
        safety = run_safety_checks(db, user_id, medicine)
        trace.append(f"Safety check: {safety}")

        if safety["status"] == "blocked":

            if safety["reason"] == "prescription_required":
                return {
                    "message": f"{medicine} requires a prescription. Please upload it before ordering.",
                    "trace": trace
                }

            if safety["reason"] == "recent_purchase":
                return {
                    "message": "You recently purchased this medicine. Please consult a doctor before ordering again.",
                    "trace": trace
                }

        # ⚠️ 3️⃣ DOSAGE VALIDATION
        if not dosage or dosage <= 0:
            return {
                "message": "Invalid dosage frequency provided.",
                "trace": trace
            }

        if dosage > 5:
            return {
                "message": "⚠️ Dosage seems unusually high. Please confirm with a doctor.",
                "trace": trace
            }

        # ✅ 4️⃣ EXECUTE ORDER
        result = execute_order(db, user_id, medicine, quantity, dosage)
        trace.append("Order successfully executed")

        return {
            "message": f"Order placed successfully for {medicine}.",
            "data": result,
            "trace": trace
        }

    # =====================================
    # ❌ UNKNOWN INTENT
    # =====================================
    return {
        "message": "I did not understand your request. Please try again.",
        "trace": trace
    }