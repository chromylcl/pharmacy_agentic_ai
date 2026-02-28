import os
from dotenv import load_dotenv
from groq import Groq
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are an intent classifier for a pharmacy AI system.

You MUST return ONLY valid JSON.
No explanations.
No extra text.

Intent rules:

1. If user wants to BUY or ORDER a medicine:
   -> intent = "order"

2. If user describes a SYMPTOM like:
   - I feel tired
   - I have headache
   - I have allergy
   - I have dry skin
   - My stomach hurts
   -> intent = "recommend"

3. If user asks about availability:
   - Is X available?
   - Do you have X?
   -> intent = "stock_check"

4. If user mentions emergency symptoms:
   - chest pain
   - difficulty breathing
   - severe bleeding
   -> intent = "emergency"

Otherwise:
   -> intent = "unknown"

For recommend:
{
  "intent": "recommend",
  "symptom": "extracted symptom"
}

For order:
{
  "intent": "order",
  "medicine": "medicine name",
  "quantity": number or null
}
"""

import json

def detect_intent(message: str):
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ],
        temperature=0
    )
    message_lower = message.lower()
    if any(word in message_lower for word in ["chest pain", "breathing", "bleeding"]):
        return {"intent": "emergency"}
    
    if any(word in message_lower for word in ["feel", "pain", "tired", "headache", "allergy", "skin"]):
        return {"intent": "recommend", "symptom": message}
    
    if any(word in message_lower for word in ["give me", "i need", "order", "buy"]):
        return {"intent": "order", "medicine": message, "quantity": None}
    


    raw = completion.choices[0].message.content.strip()

    try:
        data = json.loads(raw)

        # Whitelist allowed keys
        allowed_keys = {"intent", "symptom", "medicine", "quantity", "dosage_frequency"}

        clean_data = {k: v for k, v in data.items() if k in allowed_keys}

        return clean_data

    except Exception:
        return {"intent": "unknown"}