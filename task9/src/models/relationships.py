"""
Модуль для установки явных связей между моделями SQLAlchemy.

- `relationship()` — для объявления связи;
- `foreign()` — для явного указания, какие колонки выступают в роли внешних ключей;
- `primaryjoin` — для описания условия соединения между таблицами.

Этот файл должен импортироваться **после** определения всех моделей,
чтобы избежать ошибок импорта.
"""

from sqlalchemy.orm import relationship, foreign
from .sflight import SFlight
from .spfli import SPFli
from .sbook import SBook


# Реализует соответствие рейса и его расписания по составному ключу.
SFlight.schedules = relationship(
    "SPFli",
    back_populates="flight",
    primaryjoin=(
        (SFlight.carrid == foreign(SPFli.carrid)) &
        (SFlight.connid == foreign(SPFli.connid)) &
        (SFlight.fldate == foreign(SPFli.fldate))
    )
)

SPFli.flight = relationship(
    "SFlight",
    back_populates="schedules",
    primaryjoin=(
        (SFlight.carrid == foreign(SPFli.carrid)) &
        (SFlight.connid == foreign(SPFli.connid)) &
        (SFlight.fldate == foreign(SPFli.fldate))
    )
)

# Каждое расписание может иметь несколько бронирований.
SPFli.bookings = relationship(
    "SBook",
    back_populates="schedule",
    primaryjoin=(
        (SPFli.carrid == foreign(SBook.carrid)) &
        (SPFli.connid == foreign(SBook.connid)) &
        (SPFli.fldate == foreign(SBook.fldate))
    )
)

SBook.schedule = relationship(
    "SPFli",
    back_populates="bookings",
    primaryjoin=(
        (SPFli.carrid == foreign(SBook.carrid)) &
        (SPFli.connid == foreign(SBook.connid)) &
        (SPFli.fldate == foreign(SBook.fldate))
    )
)