"""Database connection and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from config import settings
from models import Base

# # Create database engine sqlite database
# engine = create_engine(
#     settings.database_url,
#     connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
# )

# PostgreSQL implementation
engine = create_engine(
    settings.database_url,
    # PostgreSQL-specific connection arguments
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections every hour
    echo=settings.debug  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """Initialize database with tables."""
    create_tables()
    print("Database initialized successfully!")
