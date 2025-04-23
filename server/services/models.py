from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, Float
from datetime import datetime
from config import Base

# FileStorage Model
class FileStorage(Base):
    __tablename__ = 'file_storage'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    content = Column(LargeBinary, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    landmark = Column(String, nullable=False)

# Landmark Model
class Landmark(Base):
    __tablename__ = 'landmarks'

    id = Column(String, primary_key=True, index=True)
    landmark_name = Column(String, unique=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

# 🚫 REMOVE this line when using Supabase (or comment it out)
# Base.metadata.create_all(bind=engine)
