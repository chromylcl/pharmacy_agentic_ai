from fastapi import FastAPI
from .database import engine, SessionLocal
from .models import Base
from .routes import router
from .services import import_products_from_excel

app = FastAPI(
    title="Pharmacy Agentic AI",
    version="1.0.0"
)

# Create tables
Base.metadata.create_all(bind=engine)

# Include routes
app.include_router(router)


@app.get("/")
def root():
    return {"message": "Backend running successfully 🚀"}

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    import_products_from_excel(db)
    db.close()