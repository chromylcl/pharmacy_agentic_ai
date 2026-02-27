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

# Nutrition keywords — activates 4th agent block
NUTRITION_KEYWORDS = [
    "protein", "creatine", "supplement", "muscle",
    "workout", "whey", "pre-workout", "bcaa",
    "mass gainer", "fat burner", "vitamins"
]

# Quick action prompts [emoji, label, full prompt sent to backend]
QUICK_ACTION_PROMPTS = [
    ("💊", "Refill Request", "I need to request a medication refill"),
    ("🤒", "Symptom Checker", "I want to check my symptoms"),
    ("⚠️", "Drug Interactions", "Check my medications for interactions"),
    ("🏋️", "Supplement Check", "Analyze my fitness supplements"),
]
