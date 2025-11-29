from sqlalchemy import Column, Integer, String, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from .base import Base

class SCust(Base):
    """
    Таблица клиентов (пассажиров).

    Поля:
        mandt (str): клиентский код SAP (фиктивное значение, по умолчанию '100')
        id (int): уникальный идентификатор пассажира
        name (str): полное имя пассажира

    Связи:
        bookings — один ко многим с таблицей SBook
    """
    __tablename__ = 'scust'

    mandt = Column(String(3), primary_key=True, default='100')
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    bookings = relationship(
        "SBook",
        foreign_keys="[SBook.custom_mandt, SBook.custom_id]",
        back_populates="customer"
    )
