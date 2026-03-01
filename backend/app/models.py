from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from .database import Base


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    package_size = Column(String)
    description = Column(String)

    stock = Column(Integer, default=0)
    prescription_required = Column(Boolean, default=False)
    max_safe_dosage = Column(Integer, default=10) # Added for Step 2 Safety limit


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String)
    patient_age = Column(Integer)
    patient_gender = Column(String)
    purchase_date = Column(DateTime, default=datetime.utcnow)
    product_name = Column(String)
    quantity = Column(Integer)
    total_price = Column(Float)
    dosage_frequency = Column(Float)
    next_purchase_date = Column(DateTime) # Added for Billing Extras


class RefillAlert(Base):
    __tablename__ = "refill_alerts"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String)
    medicine_name = Column(String)
    expected_run_out = Column(DateTime)
    alert_generated_at = Column(DateTime, default=datetime.utcnow)


from sqlalchemy import Boolean, DateTime
from datetime import datetime

class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String)
    medicine_name = Column(String)
    file_path = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    approved = Column(Boolean, default=True)  # mock approval for hackathon
    extracted_text = Column(String, nullable=True)


class PendingOrder(Base):
    __tablename__ = "pending_orders"

    id = Column(Integer, primary_key=True)
    patient_id = Column(String, unique=True)
    medicine_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Patient(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True, index=True) # Typically UUID or email
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    trace_id = Column(String)
    agent_count = Column(Integer)
    execution_time = Column(Float)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)