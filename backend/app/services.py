from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import or_
from .models import Medicine, Order, RefillAlert


# =========================
# IMPORT PRODUCTS
# =========================
def import_products_from_excel(db: Session):
    df = pd.read_excel("data/products-export.xlsx")

    for _, row in df.iterrows():
        exists = db.query(Medicine).filter(Medicine.name == row["Medicine Name"]).first()
        if not exists:
            med = Medicine(
                name=row["Medicine Name"],
                price=row.get("Price", 0),
                package_size=row.get("Package Size", ""),
                description=row.get("Description", ""),
                stock=row.get("Stock", 0),
                prescription_required=row.get("Prescription Required", False)
            )
            db.add(med)

    db.commit()


# =========================
# IMPORT ORDERS
# =========================
DOSAGE_MAP = {
    "once daily": 1,
    "twice daily": 2,
    "thrice daily": 3
}

def import_products_from_excel(db: Session):
    df = pd.read_excel("data/products-export.xlsx")

    # Clean column names (removes hidden spaces + lowercase)
    df.columns = df.columns.str.strip().str.lower()

    for _, row in df.iterrows():
        exists = db.query(Medicine).filter(
            Medicine.name == row["product name"]
        ).first()

        if not exists:
            med = Medicine(
                name=row["product name"],
                price=float(row.get("price rec", 0)),
                package_size=row.get("package size", ""),
                description=row.get("descriptions", ""),

                # Mock values (since Excel doesn’t have these)
                stock=50,
                prescription_required=False
            )
            db.add(med)

    db.commit()


# =========================
# CHECK STOCK
# =========================
def check_stock(db: Session, medicine_name: str, quantity: int):
    medicine_name = medicine_name.strip().lower()

    product = db.query(Medicine).filter(
    Medicine.name.ilike(f"%{medicine_name}%")
).order_by(Medicine.name).first()

    if not product:
        return {"status": "not_found"}

    if product.stock < quantity:
        return {"status": "insufficient_stock", "available": product.stock}

    return {"status": "available", "matched_product": product.name}

# =========================
# CHECK PRESCRIPTION
# =========================
def check_prescription(db: Session, medicine_name: str):
    product = db.query(Medicine).filter(
        Medicine.name.ilike(f"%{medicine_name}%")
    ).first()

    if not product:
        return {"status": "not_found"}

    return {"prescription_required": product.prescription_required}


# =========================
# PLACE ORDER
# =========================
import requests

def place_order(db: Session, patient_id: str, medicine_name: str, quantity: int, dosage_frequency: float):
    product = db.query(Medicine).filter(
        Medicine.name.ilike(f"%{medicine_name}%")
    ).first()

    if not product:
        return {"status": "not_found"}

    product.stock -= quantity

    order = Order(
        patient_id=patient_id,
        product_name=product.name,
        quantity=quantity,
        dosage_frequency=dosage_frequency
    )

    db.add(order)
    db.commit()

    # 🔥 Webhook Trigger
    try:
        requests.post(
            "http://127.0.0.1:8000/webhook/warehouse",
            json={
                "patient_id": patient_id,
                "product": product.name,
                "quantity": quantity
            }
        )
    except:
        pass

    return {
        "status": "order_placed",
        "product": product.name
    }

# =========================
# REFILL PREDICTION
# =========================
def predict_refill(db: Session, user_id: str):
    return {"alert": "You are running low on Vitamin D. Reorder?"}

from datetime import datetime, timedelta
from .models import Order

def check_recent_purchase(db: Session, user_id: str, medicine_name: str):
    three_days_ago = datetime.utcnow() - timedelta(days=3)

    recent_order = db.query(Order).filter(
        Order.patient_id == user_id,
        Order.product_name.ilike(f"%{medicine_name}%"),
        Order.purchase_date >= three_days_ago
    ).first()

    if recent_order:
        return True

    return False
# =========================
# AUTONOMOUS SCAN
# =========================
def scan_and_generate_refill_alerts(db: Session):
    users = db.query(Order.patient_id).distinct().all()
    users = [u[0] for u in users]

    generated = []

    for user in users:
        orders = db.query(Order).filter(Order.patient_id == user).all()

        for order in orders:
            if order.dosage_frequency <= 0:
                continue

            days_supply = order.quantity / order.dosage_frequency
            run_out = order.purchase_date + timedelta(days=days_supply)

            if datetime.utcnow() >= run_out - timedelta(days=2):
                existing = db.query(RefillAlert).filter(
                    RefillAlert.patient_id == user,
                    RefillAlert.medicine_name == order.product_name
                ).first()

                if not existing:
                    alert = RefillAlert(
                        patient_id=user,
                        medicine_name=order.product_name,
                        expected_run_out=run_out
                    )
                    db.add(alert)

                    generated.append({
                        "patient_id": user,
                        "medicine": order.product_name
                    })

    db.commit()
    return generated

def recommend_from_symptom(db, symptom):
    symptom = symptom.lower()

    symptom_map = {
        "dry skin": ["urea", "cream", "lotion"],
        "tired": ["vitamin", "energie", "b12"],
        "allergy": ["antiallerg", "augentropfen"],
        "immune": ["vitamin d", "vigantol"],
        "omega": ["omega"]
    }

    keywords = []

    for key in symptom_map:
        if key in symptom:
            keywords = symptom_map[key]
            break

    if not keywords:
        return []

    results = db.query(Medicine).filter(
        or_(
            *[Medicine.name.ilike(f"%{word}%") for word in keywords],
            *[Medicine.description.ilike(f"%{word}%") for word in keywords]
        )
    ).limit(3).all()

    return results

from rapidfuzz import process
from .models import Medicine

def fuzzy_match_medicine(db, input_name: str):

    medicines = db.query(Medicine).all()
    names = [m.name for m in medicines]

    if not names:
        return None

    match = process.extractOne(input_name, names)

    # match format: (matched_string, score, index)
    if match and match[1] > 75:  # confidence threshold
        return match[0]

    return None