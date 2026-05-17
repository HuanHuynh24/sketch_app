from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def init_schema():
    with engine.begin() as connection:
        connection.execute(
            text(f'CREATE SCHEMA IF NOT EXISTS "{settings.DB_SCHEMA}"')
        )
        connection.execute(
            text('CREATE EXTENSION IF NOT EXISTS vector;')
        )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()