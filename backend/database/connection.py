# backend/database/connection.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import os
from pathlib import Path

from .models import Base

# ایجاد engine به عنوان یک شیء سطح ماژول
db_path = Path(__file__).parent / 'market.db'
db_path.parent.mkdir(parents=True, exist_ok=True)

database_url = f"sqlite:///{db_path}"
engine = create_engine(
    database_url,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

class DatabaseManager:
    _instance = None
    _engine = engine
    _session_factory = SessionLocal
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.create_tables()
    
    def create_tables(self):
        Base.metadata.create_all(self._engine)
    
    def get_session(self) -> Session:
        return self._session_factory()
    
    def get_engine(self):
        return self._engine

# ایجاد یک نمونه از مدیر دیتابیس
db_manager = DatabaseManager()

# توابع کمکی برای استفاده در سراسر برنامه
def get_db():
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def session_scope():
    """Context manager برای مدیریت خودکار session"""
    session = db_manager.get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()