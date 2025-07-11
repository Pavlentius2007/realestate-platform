# 🛡️ backend/middleware/csrf.py
"""
CSRF (Cross-Site Request Forgery) Protection Middleware
"""

import secrets
import hmac
import hashlib
from typing import List, Optional
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time

class CSRFProtection:
    """CSRF Protection класс"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode()
        self.token_expiry = 3600  # 1 час
    
    def generate_token(self, session_id: str) -> str:
        """Генерирует CSRF токен"""
        timestamp = str(int(time.time()))
        message = f"{session_id}:{timestamp}"
        
        # Создаем HMAC подпись
        signature = hmac.new(
            self.secret_key,
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{message}:{signature}"
    
    def validate_token(self, token: str, session_id: str) -> bool:
        """Валидирует CSRF токен"""
        if not token:
            return False
        
        try:
            parts = token.split(':')
            if len(parts) != 3:
                return False
            
            token_session_id, timestamp, signature = parts
            
            # Проверяем session_id
            if token_session_id != session_id:
                return False
            
            # Проверяем время жизни токена
            token_time = int(timestamp)
            if int(time.time()) - token_time > self.token_expiry:
                return False
            
            # Проверяем подпись
            expected_message = f"{token_session_id}:{timestamp}"
            expected_signature = hmac.new(
                self.secret_key,
                expected_message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except (ValueError, TypeError):
            return False

class CSRFMiddleware(BaseHTTPMiddleware):
    """CSRF Middleware для автоматической проверки"""
    
    def __init__(self, app, secret_key: str, exempt_paths: Optional[List[str]] = None):
        super().__init__(app)
        self.csrf = CSRFProtection(secret_key)
        self.exempt_paths = exempt_paths or []
        
        # Пути, которые не требуют CSRF проверки
        self.default_exempt_paths = [
            "/api/auth/login",
            "/api/auth/register", 
            "/api/auth/refresh",
            "/static/",
            "/css/",
            "/js/",
            "/images/",
            "/locales/",
            "/docs",
            "/openapi.json",
            "/lang/",
            "/favicon.ico"
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Проверяем, нужна ли CSRF защита
        if not self._requires_csrf_protection(request):
            response = await call_next(request)
            return response
        
        # Получаем session_id (создаем если нет)
        session_id = request.session.get("session_id")
        if not session_id:
            session_id = secrets.token_urlsafe(32)
            request.session["session_id"] = session_id
        
        # Генерируем CSRF токен для GET запросов
        if request.method == "GET":
            csrf_token = self.csrf.generate_token(session_id)
            request.state.csrf_token = csrf_token
            
            response = await call_next(request)
            
            # Добавляем токен в cookie
            if hasattr(response, 'set_cookie'):
                response.set_cookie(
                    key="csrf_token",
                    value=csrf_token,
                    httponly=True,
                    samesite="strict",
                    secure=request.url.scheme == "https",
                    max_age=3600
                )
            
            return response
        
        # Проверяем CSRF токен для POST/PUT/DELETE запросов
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            csrf_token = self._get_csrf_token(request)
            
            if not csrf_token or not self.csrf.validate_token(csrf_token, session_id):
                return JSONResponse(
                    status_code=403,
                    content={"detail": "CSRF token missing or invalid"}
                )
        
        response = await call_next(request)
        return response
    
    def _requires_csrf_protection(self, request: Request) -> bool:
        """Определяет, нужна ли CSRF защита для данного пути"""
        path = request.url.path
        
        # Проверяем exempt paths
        all_exempt_paths = self.exempt_paths + self.default_exempt_paths
        
        for exempt_path in all_exempt_paths:
            if path.startswith(exempt_path):
                return False
        
        # API endpoints требуют защиты (кроме auth)
        if path.startswith("/api/"):
            return True
            
        # Формы требуют защиты
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            return True
        
        return False
    
    def _get_csrf_token(self, request: Request) -> Optional[str]:
        """Получает CSRF токен из запроса"""
        # Сначала проверяем заголовок X-CSRF-Token
        token = request.headers.get("X-CSRF-Token")
        if token:
            return token
        
        # Потом проверяем cookie
        token = request.cookies.get("csrf_token")
        if token:
            return token
            
        # Наконец, проверяем form data
        if hasattr(request, '_form') and request._form:
            return request._form.get("csrf_token")
        
        return None

# 🔧 Utility функции для шаблонов
def get_csrf_token(request: Request) -> str:
    """Получает CSRF токен для использования в шаблонах"""
    return getattr(request.state, 'csrf_token', '')

def csrf_token_input(request: Request) -> str:
    """Генерирует HTML input для CSRF токена"""
    token = get_csrf_token(request)
    return f'<input type="hidden" name="csrf_token" value="{token}">' 