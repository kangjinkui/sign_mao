import logging

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.db.base import Base
from app.db.session import engine

# Ensure SQLAlchemy model metadata is registered before create_all.
from app.models import Billboard, ImportJobLog  # noqa: F401

logger = logging.getLogger(__name__)


def init_db() -> None:
    try:
        Base.metadata.create_all(bind=engine)
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
            conn.execute(text("ALTER TABLE billboards ADD COLUMN IF NOT EXISTS geom geometry(Point, 4326)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_billboards_geom ON billboards USING GIST (geom)"))
            conn.execute(
                text(
                    """
                    UPDATE billboards
                    SET geom = ST_SetSRID(ST_MakePoint(lng::double precision, lat::double precision), 4326)
                    WHERE geom IS NULL
                      AND lat IS NOT NULL
                      AND lng IS NOT NULL
                    """
                )
            )
    except OperationalError as e:
        logger.warning("DB 연결 불가 - init_db 건너뜀: %s", e)
