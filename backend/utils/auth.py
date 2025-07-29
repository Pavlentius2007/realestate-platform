# 🔐 backend/utils/auth.py
"""
Система JWT аутентификации и безопасности
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os

# 🔑 Конфигурация JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_HOURS = 24
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 30

# 🛡️ Security схема
security = HTTPBearer()

class TokenData(BaseModel):
    """Данные JWT токена"""
    user_id: int
    email: str
    exp: datetime
    iat: datetime
    token_type: str  # "access" or "refresh"

class AuthService:
    """Сервис аутентификации"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Хеширование пароля с помощью bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def create_access_token(user_id: int, email: str) -> str:
        """Создание access токена"""
        now = datetime.utcnow()
        expire = now + timedelta(hours=JWT_ACCESS_TOKEN_EXPIRE_HOURS)
        
        payload = {
            "user_id": user_id,
            "email": email,
            "exp": expire,
            "iat": now,
            "token_type": "access"
        }
        
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def create_refresh_token(user_id: int, email: str) -> str:
        """Создание refresh токена"""
        now = datetime.utcnow()
        expire = now + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        
        payload = {
            "user_id": user_id,
            "email": email,
            "exp": expire,
            "iat": now,
            "token_type": "refresh"
        }
        
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    @staticmethod
    def verify_token(token: str) -> TokenData:
        """Проверка и декодирование токена"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            # Проверяем обязательные поля
            required_fields = ["user_id", "email", "exp", "iat", "token_type"]
            for field in required_fields:
                if field not in payload:
                    raise HTTPException(status_code=401, detail=f"Invalid token: missing {field}")
            
            # Проверяем срок действия
            exp_timestamp = payload["exp"]
            if isinstance(exp_timestamp, (int, float)):
                exp_datetime = datetime.fromtimestamp(exp_timestamp)
            else:
                exp_datetime = datetime.fromisoformat(str(exp_timestamp))
                
            if exp_datetime < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Token expired")
            
            return TokenData(
                user_id=payload["user_id"],
                email=payload["email"],
                exp=exp_datetime,
                iat=datetime.fromtimestamp(payload["iat"]),
                token_type=payload["token_type"]
            )
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Token validation error: {str(e)}")
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> str:
        """Обновление access токена с помощью refresh токена"""
        token_data = AuthService.verify_token(refresh_token)
        
        if token_data.token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        # Создаем новый access токен
        return AuthService.create_access_token(token_data.user_id, token_data.email)

# 🔒 Dependency для получения текущего пользователя
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """Получение данных текущего аутентифицированного пользователя"""
    token = credentials.credentials
    return AuthService.verify_token(token)

async def get_optional_user(request: Request) -> Optional[TokenData]:
    """Получение пользователя (опционально - может быть None)"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    try:
        token = auth_header.split(" ")[1]
        return AuthService.verify_token(token)
    except:
        return None

# 🛡️ Валидация входных данных
class InputSanitizer:
    """Класс для санитизации входных данных"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 500) -> str:
        """Базовая санитизация строки"""
        if not isinstance(value, str):
            return ""
        
        # Удаляем потенциально опасные символы
        dangerous_chars = ['<', '>', '"', "'", '&', '%', ';', '(', ')', '+', 'script', 'javascript:', 'data:']
        sanitized = value
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # Ограничиваем длину
        return sanitized[:max_length].strip()
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Валидация email"""
        import re
        email = email.lower().strip()
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        return email
    
    @staticmethod
    def validate_password(password: str) -> str:
        """Валидация пароля"""
        if len(password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
        
        if len(password) > 128:
            raise HTTPException(status_code=400, detail="Password too long")
        
        return password

# 🔐 Rate Limiting (базовая реализация)
from collections import defaultdict
from time import time

class RateLimiter:
    """Простой rate limiter в памяти"""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.max_requests = 100  # максимум запросов
        self.time_window = 3600  # за час (в секундах)
    
    def is_allowed(self, identifier: str) -> bool:
        """Проверка разрешен ли запрос"""
        now = time()
        
        # Очищаем старые запросы
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < self.time_window
        ]
        
        # Проверяем лимит
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # Добавляем текущий запрос
        self.requests[identifier].append(now)
        return True
    
    def get_remaining_requests(self, identifier: str) -> int:
        """Получить количество оставшихся запросов"""
        now = time()
        recent_requests = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < self.time_window
        ]
        return max(0, self.max_requests - len(recent_requests))

# Глобальный экземпляр rate limiter
rate_limiter = RateLimiter()

def check_rate_limit(request: Request):
    """Проверка rate limit по IP адресу"""
    client_ip = request.client.host
    
    if not rate_limiter.is_allowed(client_ip):
        remaining = rate_limiter.get_remaining_requests(client_ip)
        raise HTTPException(
            status_code=429, 
            detail=f"Rate limit exceeded. Try again later. Remaining: {remaining}"
        )
    
    return True 