from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    ForeignKey,
    Boolean
)

from sqlalchemy.orm import relationship

from datetime import datetime

from database import Base


class Master(Base):
    __tablename__ = "masters"

    id = Column(
        Integer,
        primary_key=True
    )

    telegram_id = Column(
        String,
        unique=True
    )

    name = Column(
        String,
        nullable=False
    )

    role = Column(
        String,
        default="master"
    )

    active = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    clients = relationship(
        "Client",
        back_populates="master"
    )


class Client(Base):
    __tablename__ = "clients"

    id = Column(
        Integer,
        primary_key=True
    )

    client_code = Column(
        String,
        unique=True
    )

    name = Column(
        String,
        nullable=False
    )

    phone = Column(
        String,
        unique=True
    )

    photo_id = Column(
        String
    )

    haircut = Column(
        String
    )

    cosmetics = Column(
        String
    )

    notes = Column(
        Text
    )

    status = Column(
        String,
        default="Новый"
    )

    visits = Column(
        Integer,
        default=0
    )

    total_money = Column(
        Integer,
        default=0
    )

    master_id = Column(
        Integer,
        ForeignKey("masters.id")
    )

    master = relationship(
        "Master",
        back_populates="clients"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class Visit(Base):
    __tablename__ = "visits"

    id = Column(
        Integer,
        primary_key=True
    )

    client_id = Column(
        Integer,
        ForeignKey("clients.id")
    )

    service = Column(
        String
    )

    price = Column(
        Integer,
        default=0
    )

    comment = Column(
        Text
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class Payment(Base):
    __tablename__ = "payments"

    id = Column(
        Integer,
        primary_key=True
    )

    client_id = Column(
        Integer,
        ForeignKey("clients.id")
    )

    amount = Column(
        Integer,
        default=0
    )

    description = Column(
        String
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )