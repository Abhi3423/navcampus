from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Supabase PostgreSQL database URL 
DATABASE_URL = os.getenv("DATABASE_URL")

# Initialize SQLAlchemy components
Base = declarative_base()

# Create engine with SSL required by Supabase
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "sslmode": "require"
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

