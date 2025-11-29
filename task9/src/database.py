"""
Модуль для настройки подключения к базе данных.

Отвечает за:
- Инициализацию движка SQLAlchemy;
- Настройку сессии для взаимодействия с БД;
- Определение базового класса для моделей;
- Предоставление зависимости `get_db` для FastAPI.


Настройка параметров подключения осуществляется через переменные окружения:
- `POSTGRES_USER` — имя пользователя PostgreSQL (по умолчанию: `"user"`);
- `POSTGRES_PASSWORD` — пароль (по умолчанию: `"password"`);
- `DB_HOST` — хост БД (по умолчанию: `"db"` — имя сервиса в Docker);
- `POSTGRES_DB` — имя базы данных (по умолчанию: `"flight_booking"`).

Пример использования в роутах:
    from src.database import get_db
    @app.get("/items")
    def read_items(db: Session = Depends(get_db)):
        ...
"""

import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# --- Настройка подключения к базе данных ---
# Переменные окружения для конфигурации PostgreSQL
DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "db")  # В Docker-сети: имя сервиса 'db'
DB_NAME = os.getenv("POSTGRES_DB", "flight_booking")

# Формирование строки подключения
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# Инициализация движка SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)

# Настройка фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для всех моделей
Base = declarative_base()


def get_db() -> Generator:
    """
    Зависимость для FastAPI, предоставляющая сессию базы данных.

    Используется в эндпоинтах через `Depends(get_db)`:
        db: Session = Depends(get_db)

    Автоматически закрывает сессию после завершения запроса,
    даже если произошла ошибка.

    Returns:
        Generator[Session, None, None]: генератор сессии SQLAlchemy.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()