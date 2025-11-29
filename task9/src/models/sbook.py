from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from .base import Base

class SBook(Base):
    """
    Таблица бронирований.

    Поля:
        mandt (str): клиентский код SAP
        carrid, connid, fldate — составной ключ рейса (ссылка на SPFli)
        bookid (int): уникальный номер бронирования для данного рейса
        custom_id (int): ID пассажира (внешний ключ на SCust)

    Связи:
        customer — многие к одному с SCust
        schedule — многие к одному с SPFli
    """
    __tablename__ = 'sbook'
    mandt = Column(String(3), primary_key=True, default='100')
    carrid = Column(String(3), primary_key=True)
    connid = Column(String(4), primary_key=True)
    fldate = Column(DateTime, primary_key=True)
    bookid = Column(Integer, primary_key=True)

    # Составной внешний ключ: (custom_mandt, custom_id) → (scust.mandt, scust.id)
    custom_mandt = Column(String(3), default='100')
    custom_id = Column(Integer)

    __table_args__ = (
        ForeignKeyConstraint(
            ['custom_mandt', 'custom_id'],
            ['scust.mandt', 'scust.id']
        ),
    )

    customer = relationship("SCust", back_populates="bookings")
    schedule = relationship("SPFli", back_populates="bookings")