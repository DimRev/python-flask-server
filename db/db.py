import threading
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "sqlite:///db/app.db"  # Update this path as needed


class Database:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance.__init__()
        return cls._instance

    def __init__(self):
        self.engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},  # Necessary for SQLite
            pool_size=5,  # Adjust based on your application's needs
            max_overflow=10,  # Adjust based on your application's needs
        )
        self.session_local = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        )
        self.Base = declarative_base()

    def get_db(self):
        db = self.session_local()
        try:
            yield db
        finally:
            db.close()
