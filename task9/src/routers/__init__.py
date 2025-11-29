"""
Модуль агрегации маршрутов (роутеров) для FastAPI-приложения.

Данный модуль объединяет все функциональные роутеры в единый
главный маршрутизатор `main_router`, который подключается
к корневому FastAPI-приложению.
"""

from fastapi import APIRouter

# Импортируем функциональные роутеры из подмодулей
from src.routers.auth import router as auth_router
from src.routers.flights import router as flights_router
from src.routers.bookings import router as bookings_router

# Создаём главный маршрутизатор
main_router = APIRouter()

# Подключаем роутеры с группировкой по тегам (для Swagger UI)
main_router.include_router(
    auth_router,
    tags=["Аутентификация"],
    #prefix="/api_v1"
)
main_router.include_router(
    flights_router,
    tags=["Перелёты"],
    #prefix="/api_v1"
)
main_router.include_router(
    bookings_router,
    tags=["Бронирование"],
    #prefix="/api_v1"
)