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
        is_hinglish = any(hindi in message.lower() for hindi in ["kya", "bhai", "nahi", "hai", "dard", "saans"])
        msg = "🚨 Bhai, this sounds like a medical emergency. Please turant nearest hospital jao." if is_hinglish else "🚨 This sounds like a medical emergency. Please go to the nearest hospital immediately."
        return {
            "message": msg,
            "trace": ["[Orchestrator] Emergency keywords detected. Bypassing other agents and issuing immediate medical alert."]
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
            trace.append("[Orchestrator] User confirmed Option A. Relaying confirmation to pending order tracker.")
            medicine = pending.medicine_name
            db.delete(pending)
            db.commit()
            data = {"intent": "order", "medicine": medicine, "quantity": 1, "dosage_frequency": 1, "confirmed": True}

        elif msg_lower in ["option c", "c", "cancel", "no", "nahi chahiye", "cancel karo"]:
            trace.append("[Orchestrator] User cancelled order via Option C. Clearing session state.")
            db.delete(pending)
            db.commit()
            is_hindi = any(w in msg_lower for w in ["karo", "nahi", "chahiye"])
            msg = "Order cancel kar diya hai. Batao agar kuch aur chahiye toh!" if is_hindi else "Order cancelled. Let me know if you need anything else."
            return {"type": "text", "message": msg, "trace": trace}

        elif msg_lower in ["option b", "b", "modify", "change", "badlo"]:
            trace.append("[Orchestrator] User requested modification via Option B. Awaiting new input.")
            db.delete(pending)
            db.commit()
            is_hindi = any(w in msg_lower for w in ["badlo"])
            msg = "Theek hai, please batao aapko kaunsi dawai ya alternative order karni hai ab." if is_hindi else "Okay, please let me know what medicine or alternative you would like to order instead."
            return {"type": "text", "message": msg, "trace": trace}

        else:
            # Fallback for unrecognized pending states, clear and proceed with intent
            db.delete(pending)
            db.commit()
            data = detect_intent(message)
            trace.append(f"[Intent Agent] Analyzed fallback message. Detected: {data}")

    else:
        # =====================================================
        # 🤖 3️⃣ INTENT DETECTION
        # =====================================================
        data = detect_intent(message)
        trace.append(f"[Intent Agent] Parsed user message. Extracted parameters: {data}")
        trace.append(f"[Orchestrator] Routing flow based on '{data.get('intent', 'unknown')}' intent.")

    lang = data.get("language", "english")
    is_hinglish = lang == "hinglish"

    # =====================================================
    # 🩺 4️⃣ RECOMMEND FLOW
    # =====================================================
    if data.get("intent") == "recommend":

        symptom = data.get("symptom")

        if not symptom:
            return {
                "message": "Dost, please apna symptom thoda clearly batao." if is_hinglish else "Please describe your symptom clearly.",
                "trace": trace
            }

        recommendations = recommend_from_symptom(db, symptom)

        return {
            "message": f"Aapke symptom '{symptom}' ke hisaab se, main yeh recommend karunga:" if is_hinglish else f"Based on your symptom '{symptom}', I recommend:",
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

        trace.append(f"[Action Agent] Preparing to process order for: {medicine_input}")

        if not medicine_input:
            return {
                "type": "error",
                "message": "Arre, please thoda clearly batao kaunsi dawai chahiye?" if is_hinglish else "Please specify the medicine name clearly.",
                "trace": trace
            }
            
    # =====================================================
    # 🛒 6️⃣ CHECKOUT FLOW
    # =====================================================
    elif data.get("intent") == "checkout":
        return {
            "type": "checkout_prompt",
            "message": "Badhiya, aapka cart ready hai! Niche click karke apna order finalize kar lo." if is_hinglish else "Alright, your cart is ready! Click below to proceed to checkout and finalize your order.",
            "trace": trace
        }
    else:
        return {
            "type": "error",
            "message": "Sorry bhai, mujhe theek se samajh nahi aaya. Aapko koi dawai order karni hai ya koi recommendation chahiye?" if is_hinglish else "I'm sorry, I didn't quite understand. Are you looking to order a medicine or get a recommendation?",
            "trace": trace
        }

    import re

    cleaned = re.sub(r"\b\d+\b", "", medicine_input)

    STOPWORDS = ["i", "need", "want", "give", "me", "please", "buy", "order", "to", "a", "an"]
    tokens = cleaned.lower().split()
    filtered = " ".join([t for t in tokens if t not in STOPWORDS])

    trace.append(f"[Semantic Matcher] Normalized entity name to: '{filtered}'")

    medicine = fuzzy_match_medicine(db, filtered)

    if not medicine:
        return {
            "type": "error",
            "message": "Yeh dawai hamare paas nahi mili. Ek baar naam ki spelling check kar lo bhai." if is_hinglish else "Medicine not found. Please check spelling.",
            "trace": trace
        }

    trace.append(f"[Database Interface] Fuzzy matched to verified DB product: '{medicine}'")

    if not quantity and not data.get("confirmed"):
        pending_order = PendingOrder(patient_id=user_id, medicine_name=medicine)
        db.add(pending_order)
        db.commit()
        return {
            "type": "ask_quantity",
            "medicine": medicine,
            "message": f"Aapko {medicine} ke kitne packs chahiye?" if is_hinglish else f"How many packs of {medicine} would you like to order?",
            "trace": trace
        }

    # Fallback default if needed downstream
    quantity = quantity or 1

    if data.get("confirmed"):
        # Bypass Master Agent if user just confirmed Option A
        status = "approved"
        reason = "User confirmed Option A"
        approved_quantity = quantity
        trace.append("[Master Agent] Bypassed full safety loop due to direct user confirmation of previous suggestions.")
        master_decision = {}
    else:
        # 🤖 MASTER AGENT 7-STEP VALIDATION
        # Provide symptoms context if coming from recommend flow, else None
        symptoms = data.get("symptom", "None Provided")
        trace.append(f"[Orchestrator] Calling Master Agent to validate 7-step medical compliance for {medicine}...")
        master_decision = evaluate_master_agent(db, user_id, medicine, quantity, symptoms=symptoms, language=lang)
        
        trace.append(f"[Master Agent] Validation complete. Status: {master_decision.get('status', 'unknown').upper()}")
        if master_decision.get('reason'):
            trace.append(f"[Master Agent] Rationale: {master_decision.get('reason')}")

        # 🛑 Handle Customer Confirmation Loop (Rule 6)
        if master_decision.get("requires_confirmation"):
            # Store pending order to catch Option A/B/C on next turn
            pending_order = PendingOrder(patient_id=user_id, medicine_name=medicine)
            db.add(pending_order)
            db.commit()

            alts = master_decision.get("suggested_alternatives", [])
            opts_en = "\n\n**Do you want to proceed with:**\n- **Option A:** Proceed\n- **Option B:** Modify\n- **Option C:** Cancel"
            opts_hi = "\n\n**Aap kya karna chahenge bhai?**\n- **Option A:** Proceed (Aage badhe)\n- **Option B:** Modify (Change karein)\n- **Option C:** Cancel (Nahi chahiye)"
            msg = f"{master_decision.get('reason', '')}{opts_hi if is_hinglish else opts_en}"
            if alts:
                alt_txt = "\n\n**Kuch behtar Alternatives:**\n" if is_hinglish else "\n\n**Suggested Alternatives:**\n"
                msg += alt_txt + "\n".join([f"- **{a.get('name', 'Unknown')}**: {a.get('description', '')}" for a in alts])
                
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
        rej_msg = f"Order Reject ho gaya: {reason}" if is_hinglish else f"Order Rejected: {reason}"
        if "prescription" in reason.lower() or "rx" in reason.lower():
            return {
                "type": "prescription_required",
                "message": rej_msg,
                "medicine": medicine,
                "trace": trace + master_decision.get("trace", [])
            }
        else:
            return {
                "type": "safety_block",
                "message": rej_msg,
                "trace": trace + master_decision.get("trace", [])
            }

    elif status == "partial":
        # Calculate pricing
        product_record = db.query(Medicine).filter(Medicine.name == medicine).first()
        unit_price = float(product_record.price if product_record and product_record.price else 0.0)
        approved_quantity = int(approved_quantity)
        total_price = round(approved_quantity * unit_price, 2)

        p_msg = f"Order Partially Approve hua: {reason}\n\nKya aap isko abhi kharidna chahenge ya cart mein add karoon? Aaj koi aur dawai chahiye kya?" if is_hinglish else f"Order Partially Approved: {reason}\n\nWould you like to buy this now or add it to your cart, sir? Do you need any more medicines today?"

        return {
            "type": "order_success",
            "message": p_msg,
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

        s_msg = "Order ekdum safe aur approved hai! 🎉\n\nKya aap isko abhi kharidna chahenge ya cart mein add karoon? Aaj koi aur dawai chahiye kya?" if is_hinglish else "Order approved under compliance!\n\nWould you like to buy this now or add it to your cart, sir? Do you need any more medicines today?"

        return {
            "type": "order_success",
            "message": s_msg,
            "data": {
                "product": medicine,
                "quantity": approved_quantity,
                "total_price": total_price
            },
            "trace": trace + master_decision.get("trace", [])
        }
    

    