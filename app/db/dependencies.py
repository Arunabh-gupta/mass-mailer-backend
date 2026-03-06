import logging

from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        logger.exception("Database session rolled back because of an unhandled exception")
        raise
    finally:
        db.close()
