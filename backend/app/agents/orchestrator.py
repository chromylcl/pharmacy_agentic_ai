from .intent_agent import detect_intent
from .master_agent import evaluate_master_agent
from .action_agent import execute_order

from ..services import recommend_from_symptom, fuzzy_match_medicine
from ..models import PendingOrder, Medicine


def run_pharmacy_agent(db, user_id, message):

    trace = []

    # =====================================================
    # 🚨 1️⃣ EMERGENCY DETECTION
    # =====================================================
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

    # =====================================================
    # 🔁 2️⃣ CONTINUE PENDING ORDER (MULTI-TURN SUPPORT)
    # =====================================================
    pending = db.query(PendingOrder).filter(
        PendingOrder.patient_id == user_id
    ).first()

    if pending:
        msg_lower = message.strip().lower()

        if msg_lower.isdigit():
            quantity = int(message.strip())
            medicine = pending.medicine_name
            trace.append("Continuing pending order")
            db.delete(pending)
            db.commit()
            data = {"intent": "order", "medicine": medicine, "quantity": quantity, "dosage_frequency": 1}

        elif msg_lower in ["option a", "a", "proceed", "yes"]:
            trace.append("User confirmed Option A (Proceed)")
            medicine = pending.medicine_name
            db.delete(pending)
            db.commit()
            data = {"intent": "order", "medicine": medicine, "quantity": 1, "dosage_frequency": 1, "confirmed": True}

        elif msg_lower in ["option c", "c", "cancel", "no"]:
            trace.append("User confirmed Option C (Cancel)")
            db.delete(pending)
            db.commit()
            return {"type": "text", "message": "Order cancelled. Let me know if you need anything else.", "trace": trace}

        elif msg_lower in ["option b", "b", "modify"]:
            trace.append("User confirmed Option B (Modify)")
            db.delete(pending)
            db.commit()
            return {"type": "text", "message": "Okay, please let me know what medicine or alternative you would like to order instead.", "trace": trace}

        else:
            # Fallback for unrecognized pending states, clear and proceed with intent
            db.delete(pending)
            db.commit()
            data = detect_intent(message)
            trace.append(f"Intent detected (after clearing pending): {data}")

    else:
        # =====================================================
        # 🤖 3️⃣ INTENT DETECTION
        # =====================================================
        data = detect_intent(message)
        trace.append(f"Intent detected: {data}")

    # =====================================================
    # 🩺 4️⃣ RECOMMEND FLOW
    # =====================================================
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

    # =====================================================
    # 💊 5️⃣ ORDER FLOW
    # =====================================================
    elif data.get("intent") == "order":
        quantity = data.get("quantity")
        dosage = data.get("dosage_frequency") or 1
        medicine_input = data.get("medicine")

        trace.append(f"Medicine extracted from intent: {medicine_input}")

        if not medicine_input:
            return {
                "type": "error",
                "message": "Please specify the medicine name clearly.",
                "trace": trace
            }
            
    # =====================================================
    # 🛒 6️⃣ CHECKOUT FLOW
    # =====================================================
    elif data.get("intent") == "checkout":
        return {
            "type": "checkout_prompt",
            "message": "Alright, your cart is ready! Click below to proceed to checkout and finalize your order.",
            "trace": trace
        }
    else:
        return {
            "type": "error",
            "message": "I'm sorry, I didn't quite understand. Are you looking to order a medicine or get a recommendation?",
            "trace": trace
        }

    import re

    cleaned = re.sub(r"\b\d+\b", "", medicine_input)

    STOPWORDS = ["i", "need", "want", "give", "me", "please", "buy", "order", "to", "a", "an"]
    tokens = cleaned.lower().split()
    filtered = " ".join([t for t in tokens if t not in STOPWORDS])

    trace.append(f"Cleaned medicine input: {filtered}")

    medicine = fuzzy_match_medicine(db, filtered)

    if not medicine:
        return {
            "type": "error",
            "message": "Medicine not found. Please check spelling.",
            "trace": trace
        }

    trace.append(f"Fuzzy matched medicine: {medicine}")

    if not quantity and not data.get("confirmed"):
        pending_order = PendingOrder(patient_id=user_id, medicine_name=medicine)
        db.add(pending_order)
        db.commit()
        return {
            "type": "ask_quantity",
            "medicine": medicine,
            "message": f"How many packs of {medicine} would you like to order?",
            "trace": trace
        }

    # Fallback default if needed downstream
    quantity = quantity or 1

    if data.get("confirmed"):
        # Bypass Master Agent if user just confirmed Option A
        status = "approved"
        reason = "User confirmed Option A"
        approved_quantity = quantity
        trace.append("Bypassed master agent due to user confirmation.")
        master_decision = {}
    else:
        # 🤖 MASTER AGENT 7-STEP VALIDATION
        # Provide symptoms context if coming from recommend flow, else None
        symptoms = data.get("symptom", "None Provided")
        master_decision = evaluate_master_agent(db, user_id, medicine, quantity, symptoms=symptoms)
        
        trace.append(f"Master Agent Decision: {master_decision}")

        # 🛑 Handle Customer Confirmation Loop (Rule 6)
        if master_decision.get("requires_confirmation"):
            # Store pending order to catch Option A/B/C on next turn
            pending_order = PendingOrder(patient_id=user_id, medicine_name=medicine)
            db.add(pending_order)
            db.commit()

            alts = master_decision.get("suggested_alternatives", [])
            msg = f"{master_decision.get('reason', '')}\n\n**Do you want to proceed with:**\n- **Option A:** Proceed\n- **Option B:** Modify\n- **Option C:** Cancel"
            if alts:
                msg += "\n\n**Suggested Alternatives:**\n" + "\n".join([f"- **{a.get('name', 'Unknown')}**: {a.get('description', '')}" for a in alts])
                
            return {
                "type": "text",
                "message": msg,
                "trace": trace + master_decision.get("trace", [])
            }

        status = master_decision.get("status")
        reason = master_decision.get("reason", "")
        approved_quantity = master_decision.get("approved_quantity", 0)

    if status == "rejected":
        # Check if the rejection was specifically due to a missing prescription
        if "prescription" in reason.lower() or "rx" in reason.lower():
            return {
                "type": "prescription_required",
                "message": f"Order Rejected: {reason}",
                "medicine": medicine,
                "trace": trace + master_decision.get("trace", [])
            }
        else:
            return {
                "type": "safety_block",
                "message": f"Order Rejected: {reason}",
                "trace": trace + master_decision.get("trace", [])
            }

    elif status == "partial":
        # Calculate pricing
        product_record = db.query(Medicine).filter(Medicine.name == medicine).first()
        unit_price = float(product_record.price if product_record and product_record.price else 0.0)
        approved_quantity = int(approved_quantity)
        total_price = round(approved_quantity * unit_price, 2)

        return {
            "type": "order_success",
            "message": f"Order Partially Approved: {reason}\n\nWould you like to buy this now or add it to your cart, sir? Do you need any more medicines today?",
            "data": {
                "product": medicine,
                "quantity": approved_quantity,
                "total_price": total_price
            },
            "trace": trace + master_decision.get("trace", [])
        }

    else:
        # Full approval
        product_record = db.query(Medicine).filter(Medicine.name == medicine).first()
        unit_price = float(product_record.price if product_record and product_record.price else 0.0)
        approved_quantity = int(approved_quantity)
        total_price = round(approved_quantity * unit_price, 2)

        return {
            "type": "order_success",
            "message": "Order approved under compliance!\n\nWould you like to buy this now or add it to your cart, sir? Do you need any more medicines today?",
            "data": {
                "product": medicine,
                "quantity": approved_quantity,
                "total_price": total_price
            },
            "trace": trace + master_decision.get("trace", [])
        }
    

    