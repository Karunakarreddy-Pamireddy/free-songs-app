from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Establish a localized persistent file database point
DATABASE_URL = "sqlite:///./free_songs.db"

# Create the core execution engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Setup session builders
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model class that our tables will inherit from
Base = declarative_base()

def get_db():
    """Dependency injection tool to provide clean database sessions to our API routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()