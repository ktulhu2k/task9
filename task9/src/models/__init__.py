"""
Модуль инициализации моделей данных для системы бронирования авиабилетов.

Содержит импорты всех моделей SQLAlchemy и обеспечивает корректную
регистрацию всех классов в метаданных `Base` до использования в Alembic
или ORM-запросах.

Порядок импорта критичен:
1. Сначала импортируются все модели;
2. Затем — модуль `relationships`, который устанавливает связи между ними.
"""

from .base import Base

# Импорт моделей данных
from .scust import SCust
from .sairport import SAirport
from .scarr import SCarr
from .sflight import SFlight
from .spfli import SPFli
from .sbook import SBook
from .user import User

# Установка связей между моделями (после импорта всех классов)
from . import relationships

# Экспорт публичного API модуля
__all__ = [ "Base", "SCust", "SAirport", "SCarr", "SFlight", "SPFli", "SBook", "User"]