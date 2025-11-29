"""
Модуль роутеров для управления бронированиями авиабилетов.

Реализует следующие эндпоинты:
- GET /api_v1/bookings — получение списка всех бронирований (доступно всем);
- GET /api_v1/booking/{bookid} — получение конкретного бронирования (доступно всем);
- POST /api_v1/booking — создание нового бронирования (только для авторизованных);
- DELETE /api_v1/booking/{bookid} — удаление бронирования (только владелец).

Все операции взаимодействуют с моделями:
- SBook — основная таблица бронирований;
- SPFli — расписание маршрутов;
- SFlight — рейсы;
- SCarr — авиакомпании;
- User — авторизованные пользователи.

Для повышения производительности используется кэширование свободных мест через Redis.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from src.database import get_db
from src.models import SBook, SPFli, User
from src.schemas.booking import BookRequest, BookResponse, AllBookingsResponse
from src.redis_cache import get_available_seats_from_cache, set_available_seats_in_cache
from src.auth import get_current_user


router = APIRouter(
    prefix="/api_v1",
    tags=["Бронирование"],
    responses={404: {"description": "Бронирование не найдено"}},
)


@router.get(
    "/bookings",
    summary="Получить список всех бронирований",
    response_model=list[AllBookingsResponse],
    responses={200: {"description": "Список бронирований успешно получен"}}
)
def get_all_bookings(db: Session = Depends(get_db)):
    """
    Возвращает полный список бронирований.

    Доступ: **публичный** (не требует авторизации).

    Возвращает:
        Список объектов AllBookingsResponse с полями:
        - bookid, carrname, cityfrom, airpfrom, cityto, airpto,
        - fltime, price, currency.
    """
    bookings = db.query(SBook).all()
    result = []
    for book in bookings:
        spfli = book.schedule
        sflight = spfli.flight
        scarr = sflight.carrier
        result.append({
            'bookid': book.bookid,
            'carrname': scarr.carrname,
            'cityfrom': spfli.cityfrom,
            'airpfrom': spfli.airpfrom,
            'cityto': spfli.cityto,
            'airpto': spfli.airpto,
            'fltime': spfli.fltime,
            'price': str(sflight.price or '0.00'),
            'currency': sflight.currency or 'EUR'
        })
    return result


@router.get(
    "/booking/{bookid}",
    summary="Получить бронирование по ID",
    response_model=AllBookingsResponse,
    responses={
        200: {"description": "Бронирование успешно найдено"},
        404: {"description": "Бронирование с указанным ID не существует"}
    }
)
def get_booking_by_id(bookid: int, db: Session = Depends(get_db)):
    """
    Возвращает данные конкретного бронирования по его идентификатору.

    Доступ: **публичный** (не требует авторизации).

    Аргументы:
        bookid (int): Уникальный идентификатор бронирования.

    Возвращает:
        Объект AllBookingsResponse с данными бронирования.

    Ошибки:
        404: Если бронирование не найдено.
    """
    book = db.query(SBook).filter_by(bookid=bookid).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено"
        )
    spfli = book.schedule
    sflight = spfli.flight
    scarr = sflight.carrier
    return {
        'bookid': book.bookid,
        'carrname': scarr.carrname,
        'cityfrom': spfli.cityfrom,
        'airpfrom': spfli.airpfrom,
        'cityto': spfli.cityto,
        'airpto': spfli.airpto,
        'fltime': spfli.fltime,
        'price': str(sflight.price or '0.00'),
        'currency': sflight.currency or 'EUR'
    }


@router.post(
    "/booking",
    summary="Создать новое бронирование",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Бронирование успешно создано"},
        400: {"description": "Нет свободных мест на рейсе"},
        401: {"description": "Требуется авторизация"},
        404: {"description": "Рейс не найден"}
    }
)
def create_booking(
    request: BookRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Создаёт новое бронирование на указанный рейс от имени авторизованного пользователя.

    Доступ: **только для авторизованных пользователей**.

    Аргументы:
        request (BookRequest): Данные рейса (carrid, connid, fldate).
        current_user (User): Авторизованный пользователь из JWT-токена.

    Возвращает:
        Объект BookResponse с подтверждением и ID бронирования.

    Ошибки:
        401: Если пользователь не авторизован;
        404: Если рейс не найден;
        400: Если нет свободных мест.
    """
    carrid = request.carrid
    connid = request.connid
    fldate_dt = request.fldate
    cache_date_str = fldate_dt.strftime("%Y-%m-%d %H:%M:%S")

    spfli = db.query(SPFli).filter_by(
        carrid=carrid,
        connid=connid,
        fldate=fldate_dt
    ).first()

    if not spfli or not spfli.flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Рейс не найден"
        )

    sflight = spfli.flight
    available = get_available_seats_from_cache(carrid, connid, cache_date_str)
    if available is None:
        booked = len(spfli.bookings)
        available = max(0, sflight.seatsmax - booked)
        set_available_seats_in_cache(carrid, connid, cache_date_str, available)

    if available <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="На этом рейсе нет свободных мест"
        )

    # Создание бронирования, привязанного к текущему пользователю
    new_bookid = max([b.bookid for b in spfli.bookings], default=0) + 1
    booking = SBook(
        carrid=carrid,
        connid=connid,
        fldate=fldate_dt,
        bookid=new_bookid,
        custom_mandt='100',
        custom_id=current_user.id
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    # Обновление кэша
    set_available_seats_in_cache(carrid, connid, cache_date_str, available - 1)

    return {
        "message": "Бронирование успешно создано",
        "booking_id": booking.bookid
    }


@router.delete(
    "/booking/{bookid}",
    summary="Удалить бронирование",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Бронирование успешно удалено"},
        403: {"description": "Недостаточно прав (бронь принадлежит другому пользователю)"},
        404: {"description": "Бронирование не найдено"}
    }
)
def delete_booking(
    bookid: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Удаляет бронирование, если оно принадлежит текущему пользователю.

    Доступ: **только для авторизованных пользователей**.

    Аргументы:
        bookid (int): Идентификатор бронирования.
        current_user (User): Авторизованный пользователь.

    Возвращает:
        Подтверждение удаления.

    Ошибки:
        401: Если пользователь не авторизован;
        403: Если бронирование принадлежит другому пользователю;
        404: Если бронирование не найдено.
    """
    book = db.query(SBook).filter_by(bookid=bookid).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено"
        )

    if book.custom_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления"
        )

    db.delete(book)
    db.commit()
    return {"message": "Бронирование удалено"}