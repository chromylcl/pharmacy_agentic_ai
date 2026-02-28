from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_
from collections import Counter
from datetime import datetime
import os

from .database import get_db
from .models import Medicine, Order, RefillAlert, Prescription
from .services import (
    predict_refill,
    scan_and_generate_refill_alerts
)

# 🔥 NEW MULTI-AGENT ORCHESTRATOR
from .agents.orchestrator import run_pharmacy_agent

router = APIRouter()

# ===============================
# 🔎 SEARCH MEDICINES
# ===============================
@router.get("/search")
def search_medicines(query: str = Query(..., min_length=2), db: Session = Depends(get_db)):

    results = db.query(Medicine).filter(
        or_(
            Medicine.name.ilike(f"%{query}%"),
            Medicine.description.ilike(f"%{query}%")
        )
    ).limit(5).all()

    return [
        {
            "id": med.id,
            "name": med.name,
            "price": med.price,
            "package_size": med.package_size,
            "description": med.description
        }
        for med in results
    ]


# ===============================
# 🤖 CHAT (MULTI AGENT)
# ===============================
@router.post("/chat")
def chat(user_id: str, message: str, db: Session = Depends(get_db)):
    return run_pharmacy_agent(db, user_id, message)


# ===============================
# 📦 ALSO BOUGHT
# ===============================
@router.get("/also-bought/{product_name}")
def also_bought(product_name: str, db: Session = Depends(get_db)):

    patients = db.query(Order.patient_id).filter(
        Order.product_name.ilike(f"%{product_name}%")
    ).all()

    patient_ids = [p[0] for p in patients]

    if not patient_ids:
        return {"message": "No purchase history found for this product."}

    other_orders = db.query(Order.product_name).filter(
        Order.patient_id.in_(patient_ids),
        ~Order.product_name.ilike(f"%{product_name}%")
    ).all()

    product_list = [p[0] for p in other_orders]

    if not product_list:
        return {"message": "No related products found."}

    product_counts = Counter(product_list)
    top_products = product_counts.most_common(3)

    return [
        {
            "product_name": name,
            "times_bought_together": count
        }
        for name, count in top_products
    ]


# ===============================
# 📊 USER ORDER HISTORY
# ===============================
@router.get("/user/orders/{user_id}")
def get_user_orders(user_id: str, db: Session = Depends(get_db)):

    orders = db.query(Order).filter(
        Order.patient_id == user_id
    ).order_by(Order.purchase_date.desc()).all()

    if not orders:
        return {"message": "No orders found for this user."}

    return [
        {
            "product": order.product_name,
            "quantity": order.quantity,
            "dosage_frequency": order.dosage_frequency,
            "purchase_date": order.purchase_date
        }
        for order in orders
    ]


# ===============================
# 🔔 REFILL SYSTEM
# ===============================
@router.get("/admin/refill/{user_id}")
def refill_alert(user_id: str, db: Session = Depends(get_db)):
    return predict_refill(db, user_id)


@router.post("/admin/scan-refills")
def scan_refills(db: Session = Depends(get_db)):
    alerts = scan_and_generate_refill_alerts(db)
    return {
        "message": "Refill scan completed",
        "alerts_generated": alerts
    }


@router.get("/admin/refill-alerts")
def get_refill_alerts(db: Session = Depends(get_db)):
    alerts = db.query(RefillAlert).all()

    return [
        {
            "patient_id": a.patient_id,
            "medicine": a.medicine_name,
            "expected_run_out": a.expected_run_out.strftime("%Y-%m-%d")
        }
        for a in alerts
    ]


# ===============================
# 📦 INVENTORY SYSTEM
# ===============================
@router.get("/admin/inventory")
def get_inventory(db: Session = Depends(get_db)):
    medicines = db.query(Medicine).all()

    return [
        {
            "id": med.id,
            "name": med.name,
            "stock": med.stock,
            "price": med.price
        }
        for med in medicines
    ]


@router.get("/admin/low-stock")
def low_stock(threshold: int = 10, db: Session = Depends(get_db)):
    medicines = db.query(Medicine).filter(Medicine.stock <= threshold).all()

    return [
        {
            "name": med.name,
            "stock": med.stock
        }
        for med in medicines
    ]


@router.get("/debug/stock/{product_name}")
def debug_stock(product_name: str, db: Session = Depends(get_db)):

    product = db.query(Medicine).filter(
        Medicine.name.ilike(f"%{product_name}%")
    ).first()

    if not product:
        return {"status": "not_found"}

    return {
        "product": product.name,
        "current_stock": product.stock
    }


# ===============================
# 📄 PRESCRIPTION UPLOAD
# ===============================
UPLOAD_DIR = "uploaded_prescriptions"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


@router.post("/upload-prescription/{user_id}/{medicine_name}")
async def upload_prescription(
    user_id: str,
    medicine_name: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    file_location = f"{UPLOAD_DIR}/{user_id}_{medicine_name}_{file.filename}"

    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)

    prescription = Prescription(
        patient_id=user_id,
        medicine_name=medicine_name,
        file_path=file_location
    )

    db.add(prescription)
    db.commit()

    return {
        "message": "Prescription uploaded successfully.",
        "file_path": file_location
    }


# ===============================
# 🚚 WAREHOUSE WEBHOOK
# ===============================
@router.post("/webhook/warehouse")
def warehouse_webhook(payload: dict):
    print("📦 Warehouse received order:", payload)
    return {"status": "warehouse_notified"}