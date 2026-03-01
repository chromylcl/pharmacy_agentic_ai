import pandas as pd
import random
import string
import os
import sys
from datetime import datetime
from sqlalchemy.orm import Session

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.database import SessionLocal, engine, Base
from app.models import Patient, Order, RefillAlert
from app.services import scan_and_generate_refill_alerts

def generate_password(length=8):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def generate_email(name):
    # simple email generation based on name
    clean_name = "".join([c for c in str(name) if c.isalpha() or c.isspace()]).strip()
    parts = clean_name.lower().split()
    if len(parts) >= 2:
        return f"{parts[0]}.{parts[1]}@example.com"
    elif len(parts) == 1:
        return f"{parts[0]}@example.com"
    else:
        return f"user{random.randint(1000, 9999)}@example.com"

def process_historical_data():
    excel_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "Consumer Order History 1.xlsx")
    txt_output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "users.txt")
    
    print(f"Reading {excel_path}...")
    df = pd.read_excel(excel_path, skiprows=1)
    
    # Strip any whitespace from column names just in case
    df.columns = [str(c).strip() for c in df.columns]
    print(f"Columns found: {df.columns.tolist()}")

    db = SessionLocal()
    
    # Identify the actual column names from the data
    col_name = "Name" if "Name" in df.columns else df.columns[0]
    col_product = "Product Purchased" if "Product Purchased" in df.columns else df.columns[4]
    col_date = "Purchase Date" if "Purchase Date" in df.columns else df.columns[3]
    col_qty = "Quantity" if "Quantity" in df.columns else "Quantity (Packs)"
    col_price = "Price" if "Price" in df.columns else "Total Price ($)"
    col_dosage = "Dosage Frequency" if "Dosage Frequency" in df.columns else "Dosage Frequency (per day)"
    col_age = "Age"
    col_gender = "Gender"

    unique_patients = df[col_name].dropna().unique()
    credentials = []
    
    seen_emails = set([e[0] for e in db.query(Patient.email).all()])

    print(f"Processing {len(unique_patients)} unique patients...")
    for name in unique_patients:
        email = generate_email(name)
        
        base_email = email
        counter = 1
        while email in seen_emails:
            parts = base_email.split('@')
            email = f"{parts[0]}{counter}@{parts[1]}"
            counter += 1
            
        seen_emails.add(email)
        password = generate_password()
        
        patient = Patient(
            id=email,  # Using email as ID for simpler frontend integration
            name=str(name),
            email=email,
            hashed_password=password, # dummy hash for hackathon (we just use raw in onboarding mockup if needed or standard hashing)
            is_verified=True
        )
        db.add(patient)
        credentials.append((str(name), email, password))
    
    db.commit()
    print("Users saved. Processing orders...")
    
    for index, row in df.iterrows():
        try:
            name = row.get(col_name)
            product = row.get(col_product)
            if pd.isna(name) or pd.isna(product):
                continue
                
            qty = row.get(col_qty, 1)
            date_val = row.get(col_date)
            if pd.isna(date_val):
                date_val = datetime.utcnow()
                
            # Find the patient ID (email)
            patient_record = db.query(Patient).filter(Patient.name == str(name)).first()
            if not patient_record:
                continue
                
            new_order = Order(
                patient_id=patient_record.id,
                patient_age=int(row.get(col_age, 30)) if not pd.isna(row.get(col_age, 30)) else 30,
                patient_gender=str(row.get(col_gender, 'Unknown')),
                purchase_date=pd.to_datetime(date_val),
                product_name=str(product),
                quantity=int(qty) if not pd.isna(qty) else 1,
                total_price=float(row.get(col_price, 0)) if not pd.isna(row.get(col_price, 0)) else 0.0,
                dosage_frequency=float(row.get(col_dosage, 1)) if not pd.isna(row.get(col_dosage, 1)) else 1.0
            )
            db.add(new_order)
        except Exception as e:
            print(f"Error processing row {index}: {e}")
            
    db.commit()
    print("Orders saved. Generating refill alerts...")
    
    try:
        scan_and_generate_refill_alerts(db)
        print("Refill alerts generated.")
    except Exception as e:
        print(f"Error generating refill alerts: {e}")
        
    db.close()
    
    print("Writing credentials file...")
    with open(txt_output_path, "w") as f:
        f.write("--- PHARMACY USER ACCOUNTS ---\n\n")
        f.write(f"{'Patient Name':<30} | {'Email':<30} | {'Password'}\n")
        f.write("-" * 80 + "\n")
        for name, email, password in credentials:
            f.write(f"{name.strip():<30} | {email:<30} | {password}\n")
            
    print(f"Complete! Credentials written to {txt_output_path}")

if __name__ == "__main__":
    process_historical_data()
