from ..services import check_recent_purchase, check_prescription
from ..models import Prescription

def run_safety_checks(db, user_id, medicine):

    # Overdose check
    if check_recent_purchase(db, user_id, medicine):
        return {"status": "blocked", "reason": "recent_purchase"}

    # Prescription check
    prescription_required = check_prescription(db, medicine)

    if prescription_required.get("prescription_required"):
        existing = db.query(Prescription).filter(
            Prescription.patient_id == user_id,
            Prescription.medicine_name.ilike(f"%{medicine}%")
        ).first()

        if not existing:
            return {"status": "blocked", "reason": "prescription_required"}

    return {"status": "safe"}