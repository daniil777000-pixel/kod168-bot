from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)
Base = declarative_base()

def get_db():
    """Возвращает сессию базы данных"""
    return SessionLocal()

def create_tables():
    """Создаёт все таблицы в базе данных"""
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы успешно")

def drop_tables():
    """Удаляет все таблицы (для тестов)"""
    Base.metadata.drop_all(bind=engine)
    print("⚠️ Таблицы удалены")