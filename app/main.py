from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.base import Base
from app.db.session import engine
import app.db.models
from app.routers import router_email_template, router_recruiter
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)
app.include_router(router_recruiter.router)
app.include_router(router_email_template.router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "env": settings.env,
        "debug": settings.debug,
    }


@app.get("/db-health")
def db_health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"db": "ok"}
