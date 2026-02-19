import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Sur Render : variable d'env DATABASE_URL (PostgreSQL)
# En local   : SQLite
_db_url = os.environ.get("DATABASE_URL", "sqlite:///./podotest.sqlite3")

# Render fournit parfois "postgres://..." — SQLAlchemy veut "postgresql://..."
if _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql://", 1)

_connect_args = {"check_same_thread": False} if _db_url.startswith("sqlite") else {}

engine = create_engine(_db_url, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
