from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, Float
from datetime import datetime
from config import Base, engine

# FileStorage Model
class FileStorage(Base):
    __tablename__ = 'file_storage'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # 'image' or 'text'
    content = Column(LargeBinary, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    landmark = Column(String, nullable=False)  # New column for landmark

# Landmark Model
class Landmark(Base):
    __tablename__ = 'landmarks'

    id = Column(String, primary_key=True, index=True)
    landmark_name = Column(String, unique=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)
