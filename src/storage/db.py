"""Database connection and session management."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base


def get_database_url() -> str:
    """Build database URL from environment or config."""
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', 'postgres')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'tokenselect')

    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def get_sqlite_url() -> str:
    """Get SQLite URL for local development/testing."""
    return "sqlite:///./tokenselect.db"


class Database:
    """Database manager class."""

    def __init__(self, use_sqlite: bool = True):
        self.use_sqlite = use_sqlite
        self.engine = None
        self.SessionLocal = None

    def connect(self):
        """Initialize database connection."""
        if self.use_sqlite:
            url = get_sqlite_url()
        else:
            url = get_database_url()

        self.engine = create_engine(
            url,
            echo=os.getenv('SQL_ECHO', 'false').lower() == 'true'
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        return self

    def create_tables(self):
        """Create all database tables."""
        if self.engine:
            Base.metadata.create_all(bind=self.engine)
        return self

    def get_session(self) -> Session:
        """Get a new database session."""
        if not self.SessionLocal:
            self.connect()
        return self.SessionLocal()

    def close(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()


# Global database instance
db = Database(use_sqlite=True)


def init_db():
    """Initialize database with tables."""
    db.connect().create_tables()
    return db


def get_db() -> Session:
    """Dependency for FastAPI to get database session."""
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()
