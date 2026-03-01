from fastapi import APIRouter

router = APIRouter()

@router.post("/warehouse")
def warehouse_webhook(order: dict):
    print("Warehouse triggered:", order)
    return {"status": "received"}