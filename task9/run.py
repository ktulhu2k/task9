"""
Точка входа для запуска FastAPI-приложения.

Пример запуска:
    python run.py
"""

import uvicorn


if __name__ == "__main__":
    uvicorn.run('src.main:app', reload=True)