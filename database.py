from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///kod168.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()  # <--- Base создаётся ЗДЕСЬ

def get_db():
    return SessionLocal()

def create_tables():
    Base.metadata.create_all(bind=engine)