# 🚦 backend/middleware/rate_limit.py
"""
Rate Limiting Middleware для защиты от злоупотреблений
"""

import time
import json
from typing import Dict, Optional, List
from collections import defaultdict, deque
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import asyncio
from dataclasses import dataclass
from enum import Enum

class RateLimitType(Enum):
    """Типы ограничений скорости"""
    REQUESTS_PER_MINUTE = "requests_per_minute"
    REQUESTS_PER_HOUR = "requests_per_hour"
    REQUESTS_PER_DAY = "requests_per_day"
    BURST = "burst"

@dataclass
class RateLimitRule:
    """Правило ограничения скорости"""
    limit: int
    window: int  # в секундах
    rule_type: RateLimitType
    paths: List[str]
    methods: List[str]
    
class RateLimiter:
    """Продвинутый Rate Limiter"""
    
    def __init__(self):
        # Хранилище для отслеживания запросов
        self.requests = defaultdict(lambda: defaultdict(deque))
        self.blocked_ips = {}  # IP -> время разблокировки
        self.warnings = defaultdict(int)  # IP -> количество предупреждений
        
        # Правила по умолчанию
        self.rules = [
            # Общие API endpoints
            RateLimitRule(
                limit=100,
                window=3600,  # 1 час
                rule_type=RateLimitType.REQUESTS_PER_HOUR,
                paths=["/api/"],
                methods=["GET", "POST", "PUT", "DELETE"]
            ),
            
            # Аутентификация (более строгие ограничения)
            RateLimitRule(
                limit=10,
                window=300,  # 5 минут
                rule_type=RateLimitType.REQUESTS_PER_MINUTE,
                paths=["/api/auth/login", "/api/auth/register"],
                methods=["POST"]
            ),
            
            # Поиск и фильтрация
            RateLimitRule(
                limit=50,
                window=60,  # 1 минута
                rule_type=RateLimitType.REQUESTS_PER_MINUTE,
                paths=["/api/search", "/api/filter"],
                methods=["GET", "POST"]
            ),
            
            # Burst protection для всех endpoints
            RateLimitRule(
                limit=20,
                window=60,  # 1 минута
                rule_type=RateLimitType.BURST,
                paths=["*"],
                methods=["*"]
            )
        ]
    
    def get_client_identifier(self, request: Request) -> str:
        """Получает идентификатор клиента (IP или user_id)"""
        # Сначала пытаемся получить реальный IP
        real_ip = request.headers.get("X-Real-IP") or \
                  request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or \
                  (request.client.host if request.client else "127.0.0.1")
        
        # Если есть аутентифицированный пользователь, используем его ID
        if hasattr(request.state, 'user_id'):
            return f"user_{request.state.user_id}"
        
        return f"ip_{real_ip}"
    
    def is_blocked(self, client_id: str) -> bool:
        """Проверяет, заблокирован ли клиент"""
        if client_id in self.blocked_ips:
            if time.time() < self.blocked_ips[client_id]:
                return True
            else:
                del self.blocked_ips[client_id]
        return False
    
    def add_request(self, client_id: str, rule: RateLimitRule):
        """Добавляет запрос в счетчик"""
        now = time.time()
        rule_key = f"{rule.rule_type.value}_{rule.window}"
        
        # Добавляем временную метку
        self.requests[client_id][rule_key].append(now)
        
        # Очищаем старые записи
        cutoff = now - rule.window
        while (self.requests[client_id][rule_key] and 
               self.requests[client_id][rule_key][0] < cutoff):
            self.requests[client_id][rule_key].popleft()
    
    def get_request_count(self, client_id: str, rule: RateLimitRule) -> int:
        """Получает количество запросов за указанное время"""
        rule_key = f"{rule.rule_type.value}_{rule.window}"
        return len(self.requests[client_id][rule_key])
    
    def check_rate_limit(self, request: Request) -> Optional[dict]:
        """Проверяет ограничения скорости"""
        client_id = self.get_client_identifier(request)
        path = request.url.path
        method = request.method
        
        # Проверяем, заблокирован ли клиент
        if self.is_blocked(client_id):
            return {
                "blocked": True,
                "message": "IP temporarily blocked due to rate limit violations",
                "retry_after": int(self.blocked_ips[client_id] - time.time())
            }
        
        # Проверяем каждое правило
        for rule in self.rules:
            if self.rule_applies(rule, path, method):
                current_count = self.get_request_count(client_id, rule)
                
                if current_count >= rule.limit:
                    # Увеличиваем счетчик предупреждений
                    self.warnings[client_id] += 1
                    
                    # Блокируем при превышении лимита предупреждений
                    if self.warnings[client_id] >= 3:
                        block_time = time.time() + 3600  # блокировка на час
                        self.blocked_ips[client_id] = block_time
                        return {
                            "blocked": True,
                            "message": "Rate limit exceeded. IP blocked for 1 hour",
                            "retry_after": 3600
                        }
                    
                    return {
                        "blocked": False,
                        "exceeded": True,
                        "message": f"Rate limit exceeded: {current_count}/{rule.limit} requests per {rule.window}s",
                        "retry_after": rule.window,
                        "remaining": 0
                    }
                
                # Добавляем запрос в счетчик
                self.add_request(client_id, rule)
                
                # Возвращаем информацию о лимитах
                return {
                    "blocked": False,
                    "exceeded": False,
                    "current": current_count + 1,
                    "limit": rule.limit,
                    "remaining": rule.limit - current_count - 1,
                    "reset_time": int(time.time() + rule.window)
                }
        
        return None
    
    def rule_applies(self, rule: RateLimitRule, path: str, method: str) -> bool:
        """Проверяет, применяется ли правило к данному запросу"""
        # Проверяем методы
        if "*" not in rule.methods and method not in rule.methods:
            return False
        
        # Проверяем пути
        if "*" in rule.paths:
            return True
        
        for rule_path in rule.paths:
            if path.startswith(rule_path):
                return True
        
        return False
    
    def get_stats(self) -> dict:
        """Получает статистику по ограничениям"""
        stats = {
            "total_clients": len(self.requests),
            "blocked_ips": len(self.blocked_ips),
            "warnings": len(self.warnings),
            "top_clients": []
        }
        
        # Топ клиентов по количеству запросов
        client_requests = {}
        for client_id, rules in self.requests.items():
            total = sum(len(requests) for requests in rules.values())
            client_requests[client_id] = total
        
        stats["top_clients"] = sorted(
            client_requests.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        return stats

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware для ограничения скорости запросов"""
    
    def __init__(self, app, enable_rate_limiting: bool = True):
        super().__init__(app)
        self.rate_limiter = RateLimiter()
        self.enabled = enable_rate_limiting
        
        # Пути, которые не требуют rate limiting
        self.exempt_paths = [
            "/static/",
            "/css/",
            "/js/",
            "/images/",
            "/favicon.ico",
            "/docs",
            "/openapi.json"
        ]
    
    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)
        
        # Проверяем exempt paths
        if any(request.url.path.startswith(path) for path in self.exempt_paths):
            return await call_next(request)
        
        # Проверяем rate limit
        result = self.rate_limiter.check_rate_limit(request)
        
        if result:
            if result.get("blocked") or result.get("exceeded"):
                response = JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": result["message"],
                        "retry_after": result["retry_after"]
                    }
                )
                
                # Добавляем заголовки rate limit
                response.headers["X-RateLimit-Limit"] = str(result.get("limit", 0))
                response.headers["X-RateLimit-Remaining"] = str(result.get("remaining", 0))
                response.headers["X-RateLimit-Reset"] = str(result.get("reset_time", 0))
                response.headers["Retry-After"] = str(result["retry_after"])
                
                return response
        
        # Выполняем запрос
        response = await call_next(request)
        
        # Добавляем заголовки rate limit в успешный ответ
        if result and not result.get("blocked") and not result.get("exceeded"):
            response.headers["X-RateLimit-Limit"] = str(result.get("limit", 0))
            response.headers["X-RateLimit-Remaining"] = str(result.get("remaining", 0))
            response.headers["X-RateLimit-Reset"] = str(result.get("reset_time", 0))
        
        return response

# 📊 Функции для мониторинга
def get_rate_limit_stats() -> dict:
    """Получает статистику rate limiting"""
    # Эта функция должна быть доступна глобально
    return {
        "message": "Rate limiting statistics",
        "note": "Implement connection to middleware instance"
    } 