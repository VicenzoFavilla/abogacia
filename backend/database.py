from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config import DATABASE_URL

# SQLite necesita check_same_thread=False; PostgreSQL no lo requiere
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency de FastAPI para inyectar sesión de BD."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
