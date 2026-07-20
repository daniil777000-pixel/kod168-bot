from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime

from database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)

    # Основная информация
    name = Column(String, nullable=False)
    phone = Column(String, unique=True)

    # Фото клиента Telegram
    photo_id = Column(String)

    # Уникальный код клиента
    client_code = Column(String, unique=True)

    # Данные по стрижке
    haircut = Column(String)
    cosmetics = Column(String)

    # Заметки мастера
    notes = Column(Text)

    # Статистика
    visits = Column(Integer, default=0)
    total_money = Column(Integer, default=0)

    # Статус клиента
    status = Column(String, default="Новый")

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )