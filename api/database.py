from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class Convention(Base):
    __tablename__ = "conventions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    idcc = Column(String, index=True, nullable=True)
    brochure = Column(String, nullable=True)
    url = Column(String)
    pdf_url = Column(String, nullable=True)
    signature_date = Column(String, nullable=True)
    extension_date = Column(String, nullable=True)
    jo_date = Column(String, nullable=True)
    sections = Column(JSON)
    toc = Column(JSON, nullable=True)
    status = Column(String, default="pending")
    extracted_at = Column(DateTime, nullable=True)
    reformulated_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    version_hash = Column(String, nullable=True)
    last_modified = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConventionChange(Base):
    __tablename__ = "convention_changes"
    
    id = Column(Integer, primary_key=True, index=True)
    convention_id = Column(Integer, index=True)
    change_date = Column(DateTime, default=datetime.utcnow, index=True)
    old_hash = Column(String)
    new_hash = Column(String)
    change_type = Column(String, default="content_modified")
    details = Column(JSON, nullable=True)
    processed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


# Database setup
import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./conventions.db")

# Configuration selon type de base
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(DATABASE_URL)
else:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
