# 🔐 backend/routers/auth.py
"""
Роуты для аутентификации пользователей
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.database import get_db
from backend.models.user import User
from backend.schemas.auth import (
    UserRegister, UserLogin, TokenResponse, RefreshTokenRequest,
    UserProfile, UserUpdate, PasswordChangeRequest
)
from backend.utils.auth import (
    AuthService, get_current_user, get_optional_user, check_rate_limit,
    InputSanitizer, TokenData
)
from backend.config.templates import templates

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
async def register_user(
    request: Request,
    user_data: UserRegister, 
    db: Session = Depends(get_db)
):
    """Регистрация нового пользователя"""
    # Проверяем rate limit
    check_rate_limit(request)
    
    # Санитизация входных данных
    email = InputSanitizer.validate_email(user_data.email)
    password = InputSanitizer.validate_password(user_data.password)
    full_name = InputSanitizer.sanitize_string(user_data.full_name or "", 200)
    phone = InputSanitizer.sanitize_string(user_data.phone or "", 20)
    
    # Проверяем существует ли пользователь
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="Пользователь с таким email уже существует"
        )
    
    try:
        # Хешируем пароль
        hashed_password = AuthService.hash_password(password)
        
        # Создаем пользователя
        new_user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name if full_name else None,
            phone=phone if phone else None,
            name=full_name if full_name else "Пользователь",
            source="website_registration",
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Создаем токены
        access_token = AuthService.create_access_token(new_user.id, new_user.email)
        refresh_token = AuthService.create_refresh_token(new_user.id, new_user.email)
        
        # Создаем профиль для ответа
        user_profile = UserProfile(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            phone=new_user.phone,
            created_at=new_user.created_at,
            is_active=new_user.is_active
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=24 * 3600,  # 24 часа в секундах
            user=user_profile
        )
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Ошибка при создании пользователя. Возможно, email уже используется."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(
    request: Request,
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Вход пользователя"""
    # Проверяем rate limit
    check_rate_limit(request)
    
    # Санитизация входных данных
    email = InputSanitizer.validate_email(login_data.email)
    password = login_data.password
    
    # Ищем пользователя
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Неверный email или пароль"
        )
    
    # Проверяем пароль
    if not AuthService.verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Неверный email или пароль"
        )
    
    # Проверяем активность пользователя
    if not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="Аккаунт заблокирован"
        )
    
    try:
        # Создаем токены
        access_token = AuthService.create_access_token(user.id, user.email)
        refresh_token = AuthService.create_refresh_token(user.id, user.email)
        
        # Создаем профиль для ответа
        user_profile = UserProfile(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            created_at=user.created_at,
            is_active=user.is_active
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=24 * 3600,  # 24 часа в секундах
            user=user_profile
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании токенов: {str(e)}"
        )

@router.post("/refresh", response_model=dict)
async def refresh_token(
    request: Request,
    refresh_data: RefreshTokenRequest
):
    """Обновление access токена"""
    check_rate_limit(request)
    
    try:
        new_access_token = AuthService.refresh_access_token(refresh_data.refresh_token)
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": 24 * 3600
        }
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Не удалось обновить токен"
        )

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение профиля текущего пользователя"""
    user = db.query(User).filter(User.id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return UserProfile(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        created_at=user.created_at,
        is_active=user.is_active
    )

@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    request: Request,
    update_data: UserUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление профиля пользователя"""
    check_rate_limit(request)
    
    user = db.query(User).filter(User.id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    try:
        # Обновляем поля если они переданы
        if update_data.full_name is not None:
            user.full_name = InputSanitizer.sanitize_string(update_data.full_name, 200)
            user.name = user.full_name  # Обновляем и name
        
        if update_data.phone is not None:
            user.phone = InputSanitizer.sanitize_string(update_data.phone, 20)
        
        db.commit()
        db.refresh(user)
        
        return UserProfile(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            created_at=user.created_at,
            is_active=user.is_active
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обновлении профиля: {str(e)}"
        )

@router.post("/change-password")
async def change_password(
    request: Request,
    password_data: PasswordChangeRequest,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Смена пароля пользователя"""
    check_rate_limit(request)
    
    user = db.query(User).filter(User.id == current_user.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Проверяем текущий пароль
    if not AuthService.verify_password(password_data.current_password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Неверный текущий пароль"
        )
    
    try:
        # Валидируем и хешируем новый пароль
        new_password = InputSanitizer.validate_password(password_data.new_password)
        user.hashed_password = AuthService.hash_password(new_password)
        
        db.commit()
        
        return {"message": "Пароль успешно изменен"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при смене пароля: {str(e)}"
        )

@router.post("/logout")
async def logout_user():
    """Выход пользователя (на клиенте нужно удалить токены)"""
    return {"message": "Пользователь успешно вышел из системы"}

# 🌐 HTML страницы для аутентификации

@router.get("/login-page", response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница входа"""
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.get("/register-page", response_class=HTMLResponse)
async def register_page(request: Request):
    """Страница регистрации"""
    return templates.TemplateResponse("auth/register.html", {"request": request})

@router.get("/profile-page", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Страница профиля (требует аутентификации)"""
    return templates.TemplateResponse("auth/profile.html", {"request": request}) 