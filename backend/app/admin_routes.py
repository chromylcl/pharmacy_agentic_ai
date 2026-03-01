from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from .database import SessionLocal
from .models import Medicine, Order, RefillAlert

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# OVERVIEW
# =========================
@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    total_products = db.query(Medicine).count()
    total_orders = db.query(Order).count()
    total_patients = db.query(Order.patient_id).distinct().count()
    low_stock = db.query(Medicine).filter(Medicine.stock < 10).count()
    refill_alerts = db.query(RefillAlert).count()

    return {
        "total_products": total_products,
        "total_orders": total_orders,
        "total_patients": total_patients,
        "low_stock_items": low_stock,
        "active_refill_alerts": refill_alerts
    }


# =========================
# PDC SUMMARY
# =========================
@router.get("/pdc-summary")
def clinic_pdc(db: Session = Depends(get_db)):

    orders = db.query(Order).all()

    if not orders:
        return {"clinic_pdc": 0}

    total_days = 0
    total_covered = 0

    for order in orders:
        if order.dosage_frequency and order.quantity:
            days_supply = order.quantity / order.dosage_frequency
            total_covered += days_supply
            total_days += 30  # observation window

    pdc = (total_covered / total_days) * 100 if total_days else 0

    return {
        "clinic_pdc": round(pdc, 2)
    }


# =========================
# LOW STOCK
# =========================
@router.get("/low-stock")
def low_stock(db: Session = Depends(get_db)):
    medicines = db.query(Medicine).filter(Medicine.stock < 10).all()
    return medicines