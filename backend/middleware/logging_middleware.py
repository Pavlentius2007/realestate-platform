import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable
import uuid

from utils.logging_config import log_request, log_security_event, log_performance_event


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для логирования HTTP запросов и ответов
    """
    
    def __init__(self, app, logger_name: str = "http"):
        super().__init__(app)
        self.logger = logging.getLogger(logger_name)
        self.access_logger = logging.getLogger("access")
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Генерируем уникальный ID для запроса
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        # Записываем время начала
        start_time = time.time()
        
        # Получаем IP адрес
        ip_address = request.client.host if request.client else "unknown"
        
        # Логируем входящий запрос
        self.logger.info(
            f"➡️ {request.method} {request.url.path}",
            extra={
                'request_id': request_id,
                'ip_address': ip_address,
                'method': request.method,
                'endpoint': str(request.url),
                'user_agent': request.headers.get('user-agent', ''),
                'referer': request.headers.get('referer', ''),
            }
        )
        
        # Обработка запроса
        try:
            response = await call_next(request)
            
            # Рассчитываем время выполнения
            end_time = time.time()
            duration = end_time - start_time
            
            # Логируем ответ
            self.logger.info(
                f"⬅️ {request.method} {request.url.path} -> {response.status_code} ({duration*1000:.2f}ms)",
                extra={
                    'request_id': request_id,
                    'ip_address': ip_address,
                    'method': request.method,
                    'endpoint': str(request.url),
                    'status_code': response.status_code,
                    'response_time': round(duration * 1000, 2),
                    'user_agent': request.headers.get('user-agent', ''),
                }
            )
            
            # Логируем в access.log
            log_request(self.access_logger, request, response, start_time)
            
            # Логируем медленные запросы
            if duration > 1.0:  # Более 1 секунды
                log_performance_event(
                    self.logger, 
                    f"{request.method} {request.url.path}", 
                    duration,
                    {
                        'request_id': request_id,
                        'ip_address': ip_address,
                        'status_code': response.status_code
                    }
                )
                
            # Логируем подозрительные запросы
            if response.status_code >= 400:
                if response.status_code == 429:
                    log_security_event(
                        self.logger,
                        "rate_limit_exceeded",
                        {
                            'request_id': request_id,
                            'status_code': response.status_code,
                            'endpoint': str(request.url),
                        },
                        request
                    )
                elif response.status_code == 401:
                    log_security_event(
                        self.logger,
                        "unauthorized_access",
                        {
                            'request_id': request_id,
                            'status_code': response.status_code,
                            'endpoint': str(request.url),
                        },
                        request
                    )
                elif response.status_code == 403:
                    log_security_event(
                        self.logger,
                        "forbidden_access",
                        {
                            'request_id': request_id,
                            'status_code': response.status_code,
                            'endpoint': str(request.url),
                        },
                        request
                    )
                elif response.status_code >= 500:
                    self.logger.error(
                        f"🔥 Server error: {request.method} {request.url.path} -> {response.status_code}",
                        extra={
                            'request_id': request_id,
                            'ip_address': ip_address,
                            'method': request.method,
                            'endpoint': str(request.url),
                            'status_code': response.status_code,
                            'response_time': round(duration * 1000, 2),
                        }
                    )
            
            return response
            
        except Exception as e:
            # Логируем исключения
            end_time = time.time()
            duration = end_time - start_time
            
            self.logger.error(
                f"💥 Exception in {request.method} {request.url.path}: {str(e)}",
                extra={
                    'request_id': request_id,
                    'ip_address': ip_address,
                    'method': request.method,
                    'endpoint': str(request.url),
                    'response_time': round(duration * 1000, 2),
                    'exception': str(e),
                },
                exc_info=True
            )
            
            # Логируем как событие безопасности если это может быть атака
            if "sql" in str(e).lower() or "xss" in str(e).lower() or "script" in str(e).lower():
                log_security_event(
                    self.logger,
                    "potential_attack",
                    {
                        'request_id': request_id,
                        'exception': str(e),
                        'endpoint': str(request.url),
                    },
                    request
                )
            
            # Пробрасываем исключение дальше
            raise e


class DatabaseLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для логирования запросов к базе данных
    """
    
    def __init__(self, app, logger_name: str = "database"):
        super().__init__(app)
        self.logger = logging.getLogger(logger_name)
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Подсчитываем количество запросов к БД
        request.state.db_query_count = 0
        request.state.db_query_time = 0
        
        response = await call_next(request)
        
        # Логируем статистику запросов к БД если она есть
        if hasattr(request.state, 'db_query_count') and request.state.db_query_count > 0:
            self.logger.info(
                f"🗄️ Database queries: {request.state.db_query_count} queries in {request.state.db_query_time:.3f}s",
                extra={
                    'request_id': getattr(request.state, 'request_id', ''),
                    'endpoint': str(request.url),
                    'db_query_count': request.state.db_query_count,
                    'db_query_time': request.state.db_query_time,
                }
            )
            
            # Логируем медленные запросы к БД
            if request.state.db_query_time > 0.5:  # Более 500ms
                log_performance_event(
                    self.logger,
                    f"slow_db_queries_{request.url.path}",
                    request.state.db_query_time,
                    {
                        'request_id': getattr(request.state, 'request_id', ''),
                        'query_count': request.state.db_query_count,
                        'endpoint': str(request.url),
                    }
                )
        
        return response 