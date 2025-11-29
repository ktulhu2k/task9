"""
Основной модуль FastAPI-приложения системы бронирования авиабилетов.
"""

from fastapi import FastAPI
from src.routers import main_router

# Инициализация FastAPI-приложения с метаданными
app = FastAPI(title="Перелеты и бронирования", description="API для поиска рейсов, просмотра и управления бронированиями.",  version="0.1.0")

# Подключение главного маршрутизатора (содержит все эндпоинты)
app.include_router(main_router)