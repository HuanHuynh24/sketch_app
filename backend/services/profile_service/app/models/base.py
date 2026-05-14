from sqlalchemy.orm import declarative_base

from app.core.config import settings


Base = declarative_base()


class SchemaMixin:
    __table_args__ = {
        "schema": settings.DB_SCHEMA,
    }