"""
Database connection setup.

By default this uses SQLite (a single local file, zero setup) so you can run
the backend immediately without installing PostgreSQL. When you're ready for
PostgreSQL (as the product spec calls for), just set the DATABASE_URL
environment variable, e.g.:

    DATABASE_URL=postgresql://user:password@localhost:5432/trustvoice

...and nothing else in this file needs to change.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./trustvoice.db")

# SQLite needs this extra arg for use with FastAPI's threaded request handling.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
