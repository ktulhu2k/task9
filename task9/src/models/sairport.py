from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from .base import Base

class SAirport(Base):
    """
    Таблица аэропортов.

    Поля:
        mandt (str): клиентский код SAP
        id (int): уникальный идентификатор аэропорта
        name (str): название аэропорта или города

    Связи:
        Используется как справочник в таблицах SFlight (airpfrom_id, airpto_id)
    """
    __tablename__ = 'sairport'

    mandt = Column(String(3), primary_key=True, default='100')
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    
    departures = relationship("SFlight", foreign_keys="[SFlight.mandt, SFlight.airpfrom_id]")
    arrivals = relationship("SFlight", foreign_keys="[SFlight.mandt, SFlight.airpto_id]")