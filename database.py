"""
Database connection handling for the SwissAirDry platform.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get PostgreSQL connection details from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    f"postgresql://{os.getenv('PGUSER', 'postgres')}:{os.getenv('PGPASSWORD', 'postgres')}@{os.getenv('PGHOST', 'localhost')}:{os.getenv('PGPORT', '5432')}/{os.getenv('PGDATABASE', 'swissairdry')}"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model class
Base = declarative_base()

def get_db():
    """
    Dependency function to get a database session.
    Yields a db session and ensures it's closed when done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
