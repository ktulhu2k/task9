#!/bin/bash
set -e

echo "Ожидание готовности PostgreSQL..."

# Проверяем подключение через Python
until python -c "import psycopg2; psycopg2.connect(host='db', port=5432, user='user', password='password', dbname='flight_booking')" > /dev/null 2>&1; do
  echo "  PostgreSQL не готов. Повтор через 2 секунды..."
  sleep 2
done

echo "PostgreSQL готов."

# Остальные команды
#alembic revision --autogenerate -m "initial tables"
alembic upgrade head
python fill_data.py

echo "Запуск FastAPI..."
exec "$@"
