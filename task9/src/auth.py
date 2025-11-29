"""
Модуль аутентификации и авторизации для FastAPI-приложения.

Реализует:
- Хэширование и верификацию паролей;
- Создание и валидацию JWT-токенов;
- Получение текущего пользователя по токену.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from src.database import get_db
from src.models import User

# --- Настройки JWT-токена ---
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"  # Алгоритм подписи токена
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Время жизни токена в минутах


pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api_v1/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Сравнивает открытый пароль с хэшированным.

    Args:
        plain_password (str): Пароль в открытом виде.
        hashed_password (str): Хэш пароля из базы данных.

    Returns:
        bool: True, если пароли совпадают; иначе False.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Генерирует хэш пароля для безопасного хранения.

    Args:
        password (str): Пароль в открытом виде.

    Returns:
        str: Хэш пароля.
    """
    return pwd_context.hash(password)


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Получает пользователя из базы данных по имени.

    Args:
        db (Session): Сессия SQLAlchemy.
        username (str): Имя пользователя.

    Returns:
        User | None: Объект пользователя, если найден; иначе None.
    """
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Аутентифицирует пользователя по логину и паролю.

    Args:
        db (Session): Сессия SQLAlchemy.
        username (str): Имя пользователя.
        password (str): Пароль в открытом виде.

    Returns:
        User | None: Объект пользователя, если аутентификация успешна; иначе None.
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создаёт JWT-токен с заданными данными и временем жизни.

    Args:
        data (dict): Данные для включения в токен (обычно {"sub": username}).
        expires_delta (Optional[timedelta]): Время жизни токена.
            Если не задано — используется 15 минут.

    Returns:
        str: Закодированный JWT-токен.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user( token: str = Depends(oauth2_scheme), db: Session = Depends(get_db) ) -> User:
    """
    Получает текущего пользователя из JWT-токена.

    Используется как зависимость (Depends) в защищённых эндпоинтах.

    Args:
        token (str): JWT-токен из заголовка Authorization.
        db (Session): Сессия SQLAlchemy.

    Returns:
        User: Объект пользователя.

    Raises:
        HTTPException (401): Если токен недействителен или пользователь не найден.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user