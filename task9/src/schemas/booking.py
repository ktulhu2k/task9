"""
Pydantic-схемы, используемые для валидации запросов и формирования ответов
в разделе бронирования авиабилетов.

Схемы обеспечивают:
- строгую типизацию входных данных (например, дата и время — объект `datetime`);
- безопасную сериализацию данных из моделей SQLAlchemy в JSON;
- валидацию на стороне сервера без дополнительного кода.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal


class BookRequest(BaseModel):
    """
    Схема входных данных для создания бронирования.

    Используется в эндпоинте `POST /api_v1/booking`.

    Примечание:
        Поле `customer_name` исключено, так как бронирование привязывается
        к авторизованному пользователю через JWT-токен, а не к имени вручную.
    """
    carrid: str
    connid: str
    fldate: datetime

    class Config:
        """Конфигурация Pydantic для ORM-режима."""
        from_attributes = True


class BookResponse(BaseModel):
    """
    Схема успешного ответа после создания бронирования.

    Возвращается в эндпоинте `POST /api_v1/booking`.
    """
    message: str
    booking_id: int

    class Config:
        """Конфигурация Pydantic для ORM-режима."""
        from_attributes = True


class AllBookingsResponse(BaseModel):
    """
    Схема элемента списка всех бронирований.

    Используется в эндпоинтах:
        - `GET /api_v1/bookings` (список)
        - `GET /api_v1/booking/{bookid}` (один элемент)

    Поля `airpfrom` и `airpto` могут отсутствовать в данных БД,
    поэтому они объявлены как опциональные (`Optional[str]`).
    """
    bookid: int
    carrname: str
    cityfrom: str
    airpfrom: Optional[str] = None
    cityto: str
    airpto: Optional[str] = None
    fltime: int
    price: Decimal
    currency: str

    class Config:
        """Конфигурация Pydantic для ORM-режима."""
        from_attributes = True