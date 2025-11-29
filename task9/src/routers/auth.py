"""
Роутер для обработки операций аутентификации и регистрации пользователей.

Предоставляет эндпоинты:
- POST /api_v1/login — аутентификация по логину и паролю;
- POST /api_v1/register — регистрация нового пользователя.

Оба эндпоинта возвращают JWT-токен в формате Bearer, пригодный
для последующей авторизации в защищённых роутах (например, бронирование).

Требования безопасности:
- Пароли хэшируются с использованием алгоритма sha256_crypt;
- Токены имеют ограниченный срок жизни;
- Проверка уникальности username и email при регистрации.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from src.schemas.users import UserRegister, Token
from src.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from src.database import get_db
from src.models import User, SCust

# Создание роутера с  тегом для Swagger UI
router = APIRouter(prefix="/api_v1", tags=["Аутентификация"])


@router.post("/login", response_model=Token, summary="Аутентификация пользователя")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Аутентификация существующего пользователя.

    Принимает:
        - имя пользователя (username);
        - пароль (password).

    Возвращает:
        - access_token (JWT);
        - token_type ("bearer").

    Ошибки:
        - 401 Unauthorized: неверные учётные данные.

    Пример запроса (form-data):
        username=admin
        password=123

    Пример ответа:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=Token, summary="Регистрация нового пользователя")
def register(user: UserRegister, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя и автоматическое создание записи в SCust.

    Принимает:
        - username (уникальный);
        - email (уникальный);
        - password.

    Действия:
        1. Проверяет уникальность username и email;
        2. Хэширует пароль;
        3. Создаёт запись в таблице `users`;
        4. Создаёт соответствующую запись в `scust` (для совместимости с бизнес-логикой бронирования);
        5. Возвращает JWT-токен.

    Ошибки:
        - 400 Bad Request: пользователь с таким именем/email уже существует.

    Пример запроса:
        {
            "username": "alice",
            "email": "alice@example.com",
            "password": "secret123"
        }

    Пример ответа:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    """
    # Проверка уникальности имени пользователя
    existing_by_username = db.query(User).filter(User.username == user.username).first()
    if existing_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    
    # Проверка уникальности email
    existing_by_email = db.query(User).filter(User.email == user.email).first()
    if existing_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Хэширование пароля и создание пользователя
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        disabled=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Создание записи в SCust для совместимости с бизнес-логикой бронирования
    scust_entry = SCust(
        mandt="100",          # Стандартное значение для SAP-подобных схем
        id=db_user.id,        # Связь с ID из таблицы users
        name=db_user.username
    )
    db.add(scust_entry)
    db.commit()

    # Генерация токена для нового пользователя
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}