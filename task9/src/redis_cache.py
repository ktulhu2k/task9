"""
Модуль кэширования свободных мест через Redis.

Предоставляет функции для хранения и извлечения количества доступных мест
на конкретный рейс с использованием Redis в качестве быстрого кэша.

Особенности:
- Автоматически отключает кэширование при недоступности Redis;
- Использует TTL (время жизни) для автоматической инвалидации устаревших данных;
- Безопасен для использования даже если Redis не запущен.

Ключ кэша имеет формат:
    seats:{carrid}:{connid}:{fldate_str}
где `fldate_str` — строка в формате 'YYYY-MM-DD HH:MM:SS'.
"""

import redis
from typing import Optional

# Глобальный флаг доступности Redis
redis_available: bool = False

# Глобальный клиент Redis
redis_client: Optional[redis.Redis] = None

# Инициализация подключения к Redis
try:
    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2
    )
    redis_client.ping()  # Проверка подключения
    redis_available = True
except redis.ConnectionError as e:
    print(f"Redis недоступен: {e}. Кэширование отключено.")
except Exception as e:
    print(f"Ошибка инициализации Redis: {e}. Кэширование отключено.")


def get_available_seats_from_cache(carrid: str, connid: str, fldate_str: str) -> Optional[int]:
    """
    Получает количество свободных мест из кэша Redis.

    Args:
        carrid (str): Код авиакомпании (например, 'SU').
        connid (str): Идентификатор маршрута (например, '0001').
        fldate_str (str): Дата и время вылета в формате 'YYYY-MM-DD HH:MM:SS'.

    Returns:
        Optional[int]: Количество свободных мест или None, если:
            - Redis недоступен;
            - Значение отсутствует в кэше.
    """
    if not redis_available:
        return None

    key = f"seats:{carrid}:{connid}:{fldate_str}"
    value = redis_client.get(key)
    return int(value) if value is not None else None


def set_available_seats_in_cache( carrid: str, connid: str, fldate_str: str, count: int, ttl: int = 3600) -> None:
    """
    Сохраняет количество свободных мест в Redis с заданным временем жизни.

    Args:
        carrid (str): Код авиакомпании.
        connid (str): Идентификатор маршрута.
        fldate_str (str): Дата и время вылета.
        count (int): Количество свободных мест.
        ttl (int): Время жизни записи в секундах (по умолчанию 3600 = 1 час).
    """
    if not redis_available:
        return

    key = f"seats:{carrid}:{connid}:{fldate_str}"
    redis_client.setex(key, ttl, str(count))