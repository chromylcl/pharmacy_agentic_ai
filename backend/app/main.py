from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <-- NEW IMPORT
from .database import engine, SessionLocal
from .models import Base
from .routes import router as main_router
from .admin_routes import router as admin_router
from .services import import_products_from_excel

app = FastAPI()

# 🔥 ADD THIS CORS BLOCK TO ALLOW REACT TO CONNECT
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], # Restrict to frontend origin so allow_credentials=True works
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(main_router)  # Chat + core routes
app.include_router(admin_router, prefix="/admin", tags=["admin"])

# Create tables
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Pharmacy AI running 🚀"}

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    import_products_from_excel(db)
    db.close()