from pydantic import BaseModel

class SymptomRequest(BaseModel):
    symptom: str