import os
import sys
import json
from groq import Groq
from dotenv import load_dotenv

# Add the parent directory to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database import SessionLocal
from backend.app.models import Medicine

def generate_descriptions():
    load_dotenv()
    db = SessionLocal()
    
    medicines = db.query(Medicine).all()
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    print(f"Checking {len(medicines)} medicines for missing descriptions...")

    for med in medicines:
        if not med.description or len(med.description) < 5 or "No description" in med.description:
            print(f"Generating description for: {med.name}...")
            prompt = f"Write a single sentence, professional medical description for the product '{med.name}'. It should sound premium and informative. Do not use quotes."
            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a medical copywriter."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=60
                )
                desc = completion.choices[0].message.content.strip().strip('"')
                med.description = desc
                db.commit()
                print(f"  -> {desc}")
            except Exception as e:
                print(f"  -> Error: {e}")

    db.close()
    print("Done generating descriptions!")

if __name__ == "__main__":
    generate_descriptions()
