from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import or_
from .models import Medicine, Order, RefillAlert, Patient



# =========================
# IMPORT PRODUCTS
# =========================
def import_products_from_excel(db: Session):
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    file_path = os.path.join(BASE_DIR, "data", "products-export.xlsx")

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
    import os
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    file_path = os.path.join(BASE_DIR, "data", "products-export.xlsx")




    df = pd.read_excel(file_path)

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
# AUTONOMOUS SCAN & SMS NOTIFICATIONS
# =========================
def scan_and_generate_refill_alerts(db: Session):
    users_records = db.query(Order.patient_id).distinct().all()
    users = [u[0] for u in users_records]

    generated = []

    # 1. Dosage Cycle Alerts (Patient's supply is running low)
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
                    db.commit() # Commit to avoid duplicates across scans

                    patient = db.query(Patient).filter(Patient.id == user).first()
                    email = patient.email if patient else user

                    # Trigger Mock EMAIL Alert
                    print(f"📧 [MOCK EMAIL to {email}] Hello! Your {order.product_name} is running low based on your dosage cycle. Please repurchase soon.")

                    generated.append({
                        "patient_id": user,
                        "medicine": order.product_name,
                        "type": "dosage_refill"
                    })

    # 2. Store Low Stock Alerts for Previous Buyers
    low_stock_meds = db.query(Medicine).filter(Medicine.stock <= 10).all()
    for med in low_stock_meds:
        # find users who bought this medicine
        buyers_records = db.query(Order.patient_id).filter(Order.product_name == med.name).distinct().all()
        buyers = [b[0] for b in buyers_records]
        
        for buyer_id in buyers:
            patient = db.query(Patient).filter(Patient.id == buyer_id).first()
            email = patient.email if patient else buyer_id
            # Check if we already alerted them recently (Mocked by just printing)
            print(f"📧 [MOCK EMAIL to {email}] Notification: A previously purchased medicine ({med.name}) is running low in our store inventory. Order now to secure your refill.")
            generated.append({
                "patient_id": buyer_id,
                "medicine": med.name,
                "type": "store_low_stock"
            })
            
    # Also trigger admin alert
    for med in low_stock_meds:
        print(f"⚠️ [ADMIN ALERT] Low stock detected for {med.name} (Qty: {med.stock})")

    return generated

from sqlalchemy import or_
from .models import Medicine


from sqlalchemy import or_
from .models import Medicine


import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def recommend_from_symptom(db, symptom):
    medicines = db.query(Medicine).all()
    if not medicines:
        return []

    catalog = []
    for m in medicines:
        catalog.append(f"ID: {m.id} | Name: {m.name} | Desc: {m.description} | Price: {m.price} | Stock: {m.stock}")
        
    catalog_text = "\n".join(catalog)

    prompt = f"""
You are a medical AI matching patient symptoms to a database of medicines.
The user has the following symptom: "{symptom}"

Here is the database catalog:
{catalog_text}

Task:
Find the top 3 best matching medicines for this symptom.
Return a JSON object containing a "recommendations" array. Each object in the array must have:
"id" (integer), "name" (string), "price" (float), "stock" (integer), "reason" (string: A 1-sentence logical explanation in English).

{{
  "recommendations": [
    {{ "id": 1, "name": "...", "price": 10.0, "stock": 5, "reason": "..." }}
  ]
}}
"""
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful JSON-only API."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        data = json.loads(completion.choices[0].message.content)
        return data.get("recommendations", [])
    except Exception as e:
        print(f"Recommend error: {e}")
        return []

from rapidfuzz import process
from .models import Medicine

def fuzzy_match_medicine(db, input_name: str):

    medicines = db.query(Medicine).all()
    names = [m.name for m in medicines]

    if not names:
        return None

    match = process.extractOne(input_name, names)

    # match format: (matched_string, score, index)
    if match and match[1] >= 65:  # confidence threshold
        return match[0]

    return None