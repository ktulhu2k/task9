"""
Скрипт для заполнения базы данных тестовыми данными.

Скрипт:
- Создаёт тестовые авиакомпании, аэропорты и рейсы;
- Генерирует расписание маршрутов (SPFLI);
- Добавляет тестовых пользователей с хэшированными паролями;
- Привязывает пользователей к таблице клиентов (SCust) для совместимости с бизнес-логикой бронирования.

Запуск:
    python fill_data.py

Примечание:
    Скрипт идемпотентен: повторный запуск не приведёт к дублированию данных.
"""

import os
import sys
from datetime import datetime, timedelta
import random

from src.database import Base, engine, SessionLocal
from src.models import SCust, SAirport, SCarr, SFlight, SPFli, User
from passlib.context import CryptContext
from decimal import Decimal

# Настройка хэширования паролей (для совместимости с auth-системой)
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Хэширует пароль с использованием алгоритма sha256_crypt.

    Args:
        password (str): Открытый пароль.

    Returns:
        str: Хэш пароля.
    """
    return pwd_context.hash(password)


def main() -> None:
    """
    Основная функция заполнения базы данных тестовыми записями.

    Выполняет следующие действия:
    1. Создаёт таблицы, если они не существуют.
    2. Добавляет авиакомпании и аэропорты.
    3. Генерирует случайные рейсы и расписание.
    4. Создаёт тестовых пользователей и привязывает их к SCust.
    """

    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        # --- Добавление авиакомпаний ---
        carriers = [('SU', 'Aeroflot'), ('LH', 'Lufthansa'), ('BA', 'British Airways')]
        for carrid, name in carriers:
            if not session.query(SCarr).filter_by(carrid=carrid).first():
                session.add(SCarr(carrid=carrid, carrname=name))

        # --- Добавление аэропортов ---
        airports = [(1001, 'Moscow'), (1002, 'London'), (1003, 'Paris'), (1004, 'Berlin')]
        for aid, name in airports:
            if not session.query(SAirport).filter_by(id=aid).first():
                session.add(SAirport(id=aid, name=name))
        session.commit()

        # --- Генерация тестовых рейсов ---
        for i in range(1, 20):
            carr = random.choice(session.query(SCarr).all())
            dep = random.choice(session.query(SAirport).all())
            arr = random.choice(session.query(SAirport).all())
            while dep == arr:
                arr = random.choice(session.query(SAirport).all())

            date = datetime.now() + timedelta(days=random.randint(1, 10))
            seats = random.randint(50, 100)

            # Создание рейса
            flight = SFlight(
                carrid=carr.carrid,
                connid=f"{i:04d}",
                fldate=date,
                price=Decimal(round(random.uniform(80, 300), 2)),
                currency='EUR',
                seatsmax=seats,
                airpfrom_id=dep.id,
                airpto_id=arr.id
            )
            session.add(flight)
            session.commit()

            # Создание расписания маршрута
            spfli = SPFli(
                carrid=carr.carrid,
                connid=f"{i:04d}",
                fldate=date,
                countryfr='RU',
                cityfrom=dep.name,
                airpfrom=dep.name[:3].upper(),
                countryto='UK',
                cityto=arr.name,
                airpto=arr.name[:3].upper(),
                fltime=random.randint(90, 300)
            )
            session.add(spfli)

        print("Тестовые данные (авиакомпании, аэропорты, рейсы) успешно добавлены.")

        # --- Заполнение тестовыми пользователями ---
        test_users = [
            {"username": "admin", "email": "admin@example.com", "password": "123"},
            {"username": "user1", "email": "user1@example.com", "password": "user123"},
            {"username": "alice", "email": "alice@example.com", "password": "secret"},
        ]

        for user_data in test_users:
            # Проверка на уникальность (по username или email)
            existing = session.query(User).filter(
                (User.username == user_data["username"]) |
                (User.email == user_data["email"])
            ).first()

            if not existing:
                hashed_pw = get_password_hash(user_data["password"])
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=hashed_pw,
                    disabled=False
                )
                session.add(user)
                session.commit()
                session.refresh(user)

                # Привязка к SCust (для совместимости с моделями бизнес-логики)
                scust = SCust(
                    mandt='100',  # Соответствует структуре SAP-подобных схем
                    id=user.id,
                    name=user.username
                )
                session.add(scust)
                print(f"Добавлен пользователь: {user.username}")
            else:
                print(f"Пользователь {user_data['username']} уже существует")

        session.commit()
        print("\nВсе тестовые пользователи успешно добавлены.")

    except Exception as e:
        session.rollback()
        print(f"Ошибка при заполнении данных: {e}")
        raise

    finally:
        session.close()


if __name__ == '__main__':
    main()