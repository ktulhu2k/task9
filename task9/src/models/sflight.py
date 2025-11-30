# src/models/sflight.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Numeric,
    ForeignKeyConstraint
)
from sqlalchemy.orm import relationship
from .base import Base

class SFlight(Base):
    """
    Таблица рейсов (конкретных вылетов авиакомпании).

    Поля:
        mandt (str): клиентский код SAP
        carrid (str): код авиакомпании (внешний ключ на SCarr)
        connid (str): идентификатор маршрута
        fldate (datetime): дата и время вылета
        price (decimal): стоимость билета
        currency (str): валюта цены
        planetype (str): тип самолёта
        seatsmax (int): максимальное количество мест
        seatssocc (int): количество занятых мест (не используется в учебном проекте)
        airpfrom_id (int): ID аэропорта отправления (внешний ключ на SAirport)
        airpto_id (int): ID аэропорта прибытия (внешний ключ на SAirport)

    Связи:
        carrier — многие к одному с SCarr
        airport_from, airport_to — справочники аэропортов
        schedules — один к одному с SPFli
    """
    __tablename__ = 'sflight'

    mandt = Column(String(3), primary_key=True, default='100')
    carrid = Column(String(3), primary_key=True)
    connid = Column(String(4), primary_key=True)
    fldate = Column(DateTime, primary_key=True)

    price = Column(Numeric(10, 2))
    currency = Column(String(3))
    planetype = Column(String(10))
    seatsmax = Column(Integer)
    seatssocc = Column(Integer)

    airpfrom_id = Column(Integer)
    airpto_id = Column(Integer)

    __table_args__ = (
        ForeignKeyConstraint(['mandt', 'carrid'], ['scarr.mandt', 'scarr.carrid']),
        ForeignKeyConstraint(['mandt', 'airpfrom_id'], ['sairport.mandt', 'sairport.id']),
        ForeignKeyConstraint(['mandt', 'airpto_id'], ['sairport.mandt', 'sairport.id']),
    )
    
    carrier = relationship("SCarr", back_populates="flights", overlaps="arrivals,departures")
    airport_from = relationship("SAirport", foreign_keys=[mandt, airpfrom_id], overlaps="arrivals,carrier,departures,flights")
    airport_to = relationship("SAirport", foreign_keys=[mandt, airpto_id], overlaps="airport_from,carrier,departures,flights,arrivals")