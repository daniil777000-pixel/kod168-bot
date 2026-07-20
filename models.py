from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime

from database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)

    # Основные данные
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)

    # Фото и идентификация
    photo_id = Column(String, nullable=True)
    client_code = Column(String, unique=True, nullable=True)

    # Информация барбера
    haircut = Column(String, nullable=True)
    cosmetics = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    # CRM статистика
    visits = Column(Integer, default=0)
    total_money = Column(Integer, default=0)

    # Новый / Постоянный / VIP
    status = Column(
        String,
        default="Новый"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )