from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from .base import Base

class SPFli(Base):
    """
    Таблица расписания маршрутов (SPFLI — Schedule Flight).

    Описывает маршрут рейса: города, страны, коды аэропортов.

    Поля:
        mandt (str): клиентский код SAP
        carrid, connid, fldate — составной первичный ключ (ссылка на SFlight)
        countryfr, cityfrom, airpfrom — страна, город и код аэропорта отправления
        countryto, cityto, airpto — страна, город и код аэропорта прибытия
        fltime (int): длительность полёта в минутах

    Связи:
        flight — один к одному с SFlight
        bookings — один ко многим с SBook
    """
    __tablename__ = 'spfli'

    mandt = Column(String(3), primary_key=True, default='100')
    carrid = Column(String(3), primary_key=True)
    connid = Column(String(4), primary_key=True)
    fldate = Column(DateTime, primary_key=True)

    countryfr = Column(String(3))
    cityfrom = Column(String(20))
    airpfrom = Column(String(3))
    countryto = Column(String(3))
    cityto = Column(String(20))
    airpto = Column(String(3))
    fltime = Column(Integer)

    __table_args__ = (
        ForeignKeyConstraint(
            ['mandt', 'carrid', 'connid', 'fldate'],
            ['sflight.mandt', 'sflight.carrid', 'sflight.connid', 'sflight.fldate']
        ),
    )