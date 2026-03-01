from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from collections import Counter
from typing import List
import os

from .database import get_db
from .models import Medicine, Order, RefillAlert, Prescription
from .services import (
    predict_refill,
    scan_and_generate_refill_alerts,
)
from .agents.orchestrator import run_pharmacy_agent
from .agents.safety_agent import run_safety_checks

# ✅ ONLY ONE ROUTER
router = APIRouter()

# =====================================================
# 🤖 CHAT (MAIN ENTRY)
# =====================================================
from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_id: str
    message: str


@router.post("/chat")
def chat(data: ChatRequest, db: Session = Depends(get_db)):
    return run_pharmacy_agent(db, data.user_id, data.message)


from pydantic import BaseModel

class QuantityRequest(BaseModel):
    user_id: str
    medicine: str
    quantity: int


from pydantic import BaseModel

class QuantityRequest(BaseModel):
    user_id: str
    medicine: str
    quantity: int


@router.post("/chat/quantity")
def continue_order(data: QuantityRequest, db: Session = Depends(get_db)):
    return run_pharmacy_agent(
        db,
        data.user_id,
        str(data.quantity)
    )
# =====================================================
# 🔎 SEARCH MEDICINES
# =====================================================
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
            "stock": med.stock,
            "prescription_required": med.prescription_required
        }
        for med in results
    ]


# =====================================================
# 📦 PRODUCTS (STORE FRONT)
# =====================================================
@router.get("/products")
def get_products(db: Session = Depends(get_db)):

    medicines = db.query(Medicine).all()

    return [
        {
            "id": m.id,
            "name": m.name,
            "price": m.price,
            "stock": m.stock,
            "prescription_required": m.prescription_required
        }
        for m in medicines
    ]


# =====================================================
# 📦 FINALIZE CHECKOUT (CONFIRM ORDER)
# =====================================================

from pydantic import BaseModel

class CartItem(BaseModel):
    name: str
    quantity: int

class CheckoutRequest(BaseModel):
    patient_id: str
    items: List[CartItem]

@router.post("/finalize-checkout")
def finalize_checkout(data: CheckoutRequest, db: Session = Depends(get_db)):

    for item in data.items:

        medicine = db.query(Medicine).filter(Medicine.name == item.name).first()

        if not medicine:
            raise HTTPException(status_code=404, detail=f"{item.name} not found")

        # 1️⃣ Check stock
        if medicine.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {item.name}")

        # 2️⃣ Prescription check
        if medicine.prescription_required:
            raise HTTPException(status_code=403, detail=f"{item.name} requires prescription")

        # 3️⃣ Safety check
        safety = run_safety_checks(db, data.patient_id, medicine.name)

        if safety["status"] == "blocked":
            raise HTTPException(status_code=403, detail="Safety rule blocked this purchase")

        # 4️⃣ Deduct stock
        medicine.stock -= item.quantity

        # 5️⃣ Create order record
        new_order = Order(
            patient_id=data.patient_id,
            product_name=medicine.name,
            quantity=item.quantity,
            dosage_frequency=1
        )

        db.add(new_order)

    db.commit()

    return {
        "status": "success",
        "message": "Checkout completed safely"
    }


# =====================================================
# 📊 USER ORDER HISTORY
# =====================================================
@router.get("/user/orders/{user_id}")
def get_user_orders(user_id: str, db: Session = Depends(get_db)):

    orders = db.query(Order).filter(
        Order.patient_id == user_id
    ).order_by(Order.purchase_date.desc()).all()

    return [
        {
            "product": order.product_name,
            "quantity": order.quantity,
            "purchase_date": order.purchase_date
        }
        for order in orders
    ]


# =====================================================
# 🔔 REFILL SYSTEM
# =====================================================
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


# =====================================================
# 📦 INVENTORY SYSTEM
# =====================================================
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


# =====================================================
# 📄 PRESCRIPTION UPLOAD
# =====================================================
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


# =====================================================
# 🚚 WAREHOUSE WEBHOOK
# =====================================================
@router.post("/webhook/warehouse")
def warehouse_webhook(payload: dict):
    print("📦 Warehouse received order:", payload)
    return {"status": "warehouse_notified"}