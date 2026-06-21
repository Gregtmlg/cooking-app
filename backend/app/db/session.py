from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.core.config import settings

engine = create_engine(
    settings.database_url, 
    connect_args={"check_same_thread": False} # nécessaire pour SQLite uniquement
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()