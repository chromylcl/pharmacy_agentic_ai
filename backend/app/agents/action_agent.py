from ..services import place_order

def execute_order(db, user_id, medicine, quantity, dosage):
    return place_order(db, user_id, medicine, quantity, dosage)