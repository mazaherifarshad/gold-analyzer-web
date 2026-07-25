"""
Database Connection Manager
مدیریت اتصال به دیتابیس
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import os
from pathlib import Path

from .models import Base


class DatabaseManager:
    _instance = None
    _engine = None
    _session_factory = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._engine is None:
            self._initialize()
    
    def _initialize(self):
        db_path = Path(__file__).parent / 'market.db'
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        database_url = f"sqlite:///{db_path}"
        self._engine = create_engine(
            database_url,
            connect_args={'check_same_thread': False},
            poolclass=StaticPool,
            echo=False
        )
        self._session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine
        )
        self.create_tables()
    
    def create_tables(self):
        Base.metadata.create_all(self._engine)
    
    def get_session(self) -> Session:
        return self._session_factory()
    
    def get_engine(self):
        return self._engine


db_manager = DatabaseManager()


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