
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session


from app.config import settings
from app.database import get_db
from app.routers.auth import router as auth_router
from app.routers.patients import router as patients_router
from app.routers.appointments import router as appointments_router
from app.routers.users import router as users_router
from app.routers import care_instructions
from app.routers import reminders
from app.routers import dashboard
from app.routers import audit_logs


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Patient Follow-Up Management System",
    version="1.0.0"
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register authentication router
app.include_router(auth_router)
app.include_router(patients_router)
app.include_router(appointments_router)
app.include_router(users_router)
app.include_router(care_instructions.router)
app.include_router(reminders.router)
app.include_router(dashboard.router)
app.include_router(audit_logs.router)



# Home API
@app.get("/")
def home():

    return {
        "application": settings.APP_NAME,
        "message": "Application is running successfully"
    }


# Database health check
@app.get("/health")
def health_check(db: Session = Depends(get_db)):

    db.execute(text("SELECT 1"))

    return {
        "status": "healthy",
        "database": "MySQL connected"
    }
