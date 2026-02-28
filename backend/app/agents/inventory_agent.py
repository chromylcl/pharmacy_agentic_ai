from app.services import check_stock

def check_inventory(db, medicine, quantity):
    return check_stock(db, medicine, quantity)