import logging
import time

from fastapi import FastAPI, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.db.dependencies import get_db
import app.db.models
from app.routers import router_campaign, router_contact, router_email_template
Base.metadata.create_all(bind=engine)

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)
app.include_router(router_campaign.router)
app.include_router(router_contact.router)
app.include_router(router_email_template.router)


@app.middleware("http")
async def request_logger(request: Request, call_next):
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        logger.exception(
            "%s %s -> 500 (%sms)",
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    logger.info(
        "%s %s -> %s (%sms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


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
