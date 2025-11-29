"""
Базовый класс для всех моделей SQLAlchemy в проекте.

Этот модуль определяет единый базовый класс `Base`, от которого наследуются
все модели данных (таблицы) приложения.

Пример использования:
    from src.models.base import Base
    from sqlalchemy import Column, Integer, String

    class User(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        name = Column(String(50))
"""

from sqlalchemy.orm import declarative_base

# Создание базового класса для декларативных моделей
Base = declarative_base()