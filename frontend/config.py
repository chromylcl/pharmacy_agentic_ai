import os
from dotenv import load_dotenv

load_dotenv()

# App
APP_NAME = "Pharmacy_Assistant"
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Emergency keywords — triggers Red Route, bypasses LLM entirely
EMERGENCY_KEYWORDS = [
    "chest pain", "can't breathe", "cannot breathe",
    "severe bleeding", "overdose", "unconscious",
    "heart attack", "not breathing", "stroke",
    "allergic reaction", "anaphylaxis"
]

# Restricted drugs — triggers prescription upload screen
RESTRICTED_DRUGS = [
    "oxycodone", "adderall", "xanax", "tramadol",
    "ambien", "valium", "percocet", "morphine",
    "fentanyl", "ritalin", "klonopin"
]



# Quick action prompts [emoji, label, full prompt sent to backend]
QUICK_ACTION_PROMPTS = [
    ("💊", "Refill Request", "I need to request a medication refill"),
    ("🤒", "Symptom Checker", "I want to check my symptoms"),
    ("⚠️", "Drug Interactions", "Check my medications for interactions"),
    ("🛒", "Browse Pharmacy", "I want to browse the pharmacy store for OTC medications."),
]


# Add this list to config.py
OTC_PRODUCTS = [
    {"name": "Ibuprofen 400mg", "price": 5.99, "stock": 120, "category": "Pain Relief", "restricted": False},
    {"name": "Paracetamol 500mg", "price": 4.50, "stock": 45, "category": "Pain Relief", "restricted": False},
    {"name": "Loratadine 10mg", "price": 8.99, "stock": 0, "category": "Allergy", "restricted": False},
    {"name": "Oxycodone 10mg", "price": 25.00, "stock": 8, "category": "Pain Relief", "restricted": True}
]

