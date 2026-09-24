from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

import os

# Engine configuration
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# In serverless environments (e.g. Vercel), the root filesystem is read-only.
# Redirect SQLite database storage to /tmp/ if running in serverless and no external DB is provided.
if (os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")) and db_url.startswith("sqlite"):
    db_url = "sqlite:////tmp/skillmatch.db"

if settings.is_sqlite:
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        echo=False,
    )
else:
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            return True
    except Exception as e:
        return False
