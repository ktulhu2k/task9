from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from .base import Base

class SCarr(Base):
    """
    Таблица авиакомпаний.

    Поля:
        mandt (str): клиентский код SAP
        carrid (str): уникальный код авиакомпании (например, 'SU', 'LH')
        carrname (str): полное название авиакомпании

    Связи:
        flights — один ко многим с таблицей SFlight
    """
    __tablename__ = 'scarr'

    mandt = Column(String(3), primary_key=True, default='100')
    carrid = Column(String(3), primary_key=True)
    carrname = Column(String(200), nullable=False)

    flights = relationship("SFlight", back_populates="carrier", overlaps="arrivals,departures")