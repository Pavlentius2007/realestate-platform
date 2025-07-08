# 📄 backend/schemas/auth.py
"""
Схемы Pydantic для аутентификации
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    """Схема для регистрации пользователя"""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., min_length=6, max_length=128, description="Пароль")
    full_name: Optional[str] = Field(None, max_length=200, description="Полное имя")
    phone: Optional[str] = Field(None, max_length=20, description="Номер телефона")
    
    @validator('password')
    def validate_password_strength(cls, v):
        """Дополнительная валидация пароля"""
        if len(v.strip()) < 6:
            raise ValueError('Пароль должен содержать минимум 6 символов')
        return v.strip()
    
    @validator('full_name')
    def validate_full_name(cls, v):
        """Валидация имени"""
        if v:
            v = v.strip()
            if len(v) < 2:
                raise ValueError('Имя должно содержать минимум 2 символа')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        """Базовая валидация телефона"""
        if v:
            v = v.strip()
            # Удаляем все кроме цифр и +
            import re
            clean_phone = re.sub(r'[^\d+]', '', v)
            if len(clean_phone) < 10:
                raise ValueError('Некорректный номер телефона')
            return clean_phone
        return v

class UserLogin(BaseModel):
    """Схема для входа пользователя"""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(..., description="Пароль")

class TokenResponse(BaseModel):
    """Ответ с токенами"""
    access_token: str = Field(..., description="JWT Access токен")
    refresh_token: str = Field(..., description="JWT Refresh токен") 
    token_type: str = Field(default="bearer", description="Тип токена")
    expires_in: int = Field(..., description="Время жизни access токена в секундах")
    user: 'UserProfile' = Field(..., description="Данные пользователя")

class RefreshTokenRequest(BaseModel):
    """Запрос на обновление токена"""
    refresh_token: str = Field(..., description="Refresh токен")

class UserProfile(BaseModel):
    """Профиль пользователя (для ответов)"""
    id: int = Field(..., description="ID пользователя")
    email: EmailStr = Field(..., description="Email")
    full_name: Optional[str] = Field(None, description="Полное имя")
    phone: Optional[str] = Field(None, description="Телефон")
    created_at: datetime = Field(..., description="Дата создания")
    is_active: bool = Field(default=True, description="Активен ли пользователь")
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    """Схема для обновления профиля пользователя"""
    full_name: Optional[str] = Field(None, max_length=200, description="Полное имя")
    phone: Optional[str] = Field(None, max_length=20, description="Номер телефона")
    
    @validator('full_name')
    def validate_full_name(cls, v):
        """Валидация имени"""
        if v:
            v = v.strip()
            if len(v) < 2:
                raise ValueError('Имя должно содержать минимум 2 символа')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        """Базовая валидация телефона"""
        if v:
            v = v.strip()
            import re
            clean_phone = re.sub(r'[^\d+]', '', v)
            if len(clean_phone) < 10:
                raise ValueError('Некорректный номер телефона')
            return clean_phone
        return v

class PasswordChangeRequest(BaseModel):
    """Запрос на смену пароля"""
    current_password: str = Field(..., description="Текущий пароль")
    new_password: str = Field(..., min_length=6, max_length=128, description="Новый пароль")
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        """Дополнительная валидация пароля"""
        if len(v.strip()) < 6:
            raise ValueError('Пароль должен содержать минимум 6 символов')
        return v.strip()

class PasswordResetRequest(BaseModel):
    """Запрос на сброс пароля"""
    email: EmailStr = Field(..., description="Email для сброса пароля")

class PasswordResetConfirm(BaseModel):
    """Подтверждение сброса пароля"""
    token: str = Field(..., description="Токен сброса пароля")
    new_password: str = Field(..., min_length=6, max_length=128, description="Новый пароль")
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        """Дополнительная валидация пароля"""
        if len(v.strip()) < 6:
            raise ValueError('Пароль должен содержать минимум 6 символов')
        return v.strip()

# Обновляем forward references
TokenResponse.model_rebuild() 