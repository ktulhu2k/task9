"""
Модуль роутеров для работы с рейсами авиакомпаний.

Предоставляет эндпоинты:
- Поиск рейсов по городам отправления/прибытия и дате;
- Получение полного списка всех рейсов.

Все эндпоинты доступны без авторизации (публичный интерфейс).
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from src.database import get_db
from src.models import SPFli, SFlight
from src.schemas.flight import FlightSearchResponse


# Инициализация роутера с префиксом и тегами для Swagger UI
router = APIRouter(
    prefix="/api_v1",
    tags=["Перелёты"],
    responses={404: {"description": "Не найдено"}},
)


@router.get(
    "/search",
    summary="Поиск рейсов по маршруту и дате",
    response_model=List[FlightSearchResponse],
    response_description="Список доступных рейсов, удовлетворяющих критериям поиска"
)
def search_flights(
    from_city: str = Query(
        ...,
        min_length=1,
        description="Город или аэропорт отправления (регистронезависимый)"
    ),
    to_city: str = Query(
        ...,
        min_length=1,
        description="Город или аэропорт прибытия (регистронезависимый)"
    ),
    date: str = Query(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Дата вылета в формате ГГГГ-ММ-ДД"
    ),
    db: Session = Depends(get_db)
) -> List[FlightSearchResponse]:
    """
    Выполняет поиск рейсов по заданным критериям:
    - город отправления (`from_city`);
    - город прибытия (`to_city`);
    - дата вылета (`date`).

    Возвращает только рейсы с доступными местами.

    Параметры:
        from_city (str): Город отправления.
        to_city (str): Город прибытия.
        date (str): Дата в формате "ГГГГ-ММ-ДД".
        db (Session): Сессия SQLAlchemy (инжектируется автоматически).

    Возвращает:
        List[FlightSearchResponse]: Список найденных рейсов.

    Исключения:
        HTTPException(400): Некорректный формат даты.
    """
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Неверный формат даты. Используйте ГГГГ-ММ-ДД"
        )

    # Фильтрация рейсов по городам (регистронезависимо)
    candidates = db.query(SPFli).filter(
        SPFli.cityfrom.ilike(f"%{from_city}%"),
        SPFli.cityto.ilike(f"%{to_city}%")
    ).all()

    result = []
    for sp in candidates:
        # Пропускаем рейсы, не соответствующие дате
        if sp.fldate.date() != target_date:
            continue

        sflight = sp.flight
        if not sflight:
            continue

        # Рассчитываем доступные места
        booked = len(sp.bookings)
        available = max(0, sflight.seatsmax - booked)
        if available <= 0:
            continue

        result.append({
            'carrid': sp.carrid,
            'connid': sp.connid,
            'fldate': sp.fldate.isoformat(),
            'cityfrom': sp.cityfrom,
            'cityto': sp.cityto,
            'available_seats': available,
            'price': str(sflight.price or '0.00'),
            'currency': sflight.currency or 'EUR'
        })

    return result


@router.get(
    "/flights",
    summary="Получение полного списка всех рейсов",
    response_model=List[FlightSearchResponse],
    response_description="Список всех рейсов, отсортированный по дате вылета"
)
def get_all_flights(db: Session = Depends(get_db)) -> List[FlightSearchResponse]:
    """
    Возвращает полный список всех рейсов в системе.

    Ответ автоматически сортируется по дате вылета (по возрастанию).

    Параметры:
        db (Session): Сессия SQLAlchemy (инжектируется автоматически).

    Возвращает:
        List[FlightSearchResponse]: Список всех рейсов.
    """
    all_spflis = db.query(SPFli).all()
    result = []

    for sp in all_spflis:
        sflight = sp.flight
        if not sflight:
            continue

        booked = len(sp.bookings)
        available = max(0, sflight.seatsmax - booked)

        result.append({
            'carrid': sp.carrid,
            'connid': sp.connid,
            'fldate': sp.fldate.isoformat(),
            'cityfrom': sp.cityfrom,
            'cityto': sp.cityto,
            'available_seats': available,
            'total_seats': sflight.seatsmax,
            'price': str(sflight.price or '0.00'),
            'currency': sflight.currency or 'EUR'
        })

    # Сортировка по дате вылета
    result.sort(key=lambda x: x['fldate'])
    return result