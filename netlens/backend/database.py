import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

DB_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_PATH = os.path.join(DB_DIR, "netlens.db")
SQLITE_URL = f"sqlite:///{SQLITE_PATH}"

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/netlens_db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
elif DATABASE_URL.startswith("postgresql"):
    connect_args = {"connect_timeout": 2}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)

# Test PostgreSQL connectivity; automatically fallback to SQLite if offline
if not DATABASE_URL.startswith("sqlite"):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as ex:
        logging.info(f"PostgreSQL unreachable ({ex}). Using local SQLite database at {SQLITE_PATH}.")
        DATABASE_URL = SQLITE_URL
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    import models  # Ensure all model tables are registered with Base.metadata
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
