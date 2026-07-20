from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from database import Base  # <--- Base импортируется ИЗ database.py

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    phone = Column(String(20), nullable=True)
    birthday = Column(String(10), nullable=True)
    favorite_cut = Column(String(200), nullable=True)
    favorite_cosmetic = Column(String(200), nullable=True)
    dislikes = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    photo = Column(String(500), nullable=True)
    kod_id = Column(String(50), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_spent = Column(Float, default=0)
    visits_count = Column(Integer, default=0)

class Visit(Base):
    __tablename__ = "visits"
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer)
    service = Column(String(100))
    price = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)