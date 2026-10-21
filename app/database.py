"""Database connection setup.

SQLite stores everything in one file (vyapai.db). SQLAlchemy gives us:
  - engine:       the connection to the database
  - SessionLocal: a factory for "sessions" (one session = one unit of work / transaction)
  - Base:         parent class for all our table models
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./vyapai.db"

# check_same_thread=False is needed because FastAPI handles requests in different threads
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


# SQLite does NOT enforce foreign keys by default. This turns it on for every connection.
@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, _):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency: gives each request its own session, closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
