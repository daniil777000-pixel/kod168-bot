from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)

    name = Column(String(100), nullable=False)

    phone = Column(String(30))

    birthday = Column(String(20))

    haircut = Column(String(200))

    notes = Column(Text)

    photo = Column(String(300))

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    visits = relationship(
        "Visit",
        back_populates="client"
    )


class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True)

    client_id = Column(
        Integer,
        ForeignKey("clients.id")
    )

    service = Column(String(100))

    price = Column(Integer)

    comment = Column(Text)

    date = Column(
        DateTime,
        default=datetime.utcnow
    )

    client = relationship(
        "Client",
        back_populates="visits"
    )
