import json
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from typing import Callable

from utils.security import sanitize_form_data, check_for_attacks
from utils.logging_config import log_security_event

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware для автоматической санитизации входных данных
    """
    
    def __init__(self, app, enable_sanitization: bool = True):
        super().__init__(app)
        self.enable_sanitization = enable_sanitization
        
        # Endpoints, которые не требуют санитизации
        self.exempt_paths = [
            '/static/',
            '/css/',
            '/js/',
            '/images/',
            '/favicon.ico',
            '/robots.txt'
        ]
    
    def is_exempt_path(self, path: str) -> bool:
        """Проверка, освобожден ли путь от санитизации"""
        return any(path.startswith(exempt) for exempt in self.exempt_paths)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self.enable_sanitization or self.is_exempt_path(request.url.path):
            return await call_next(request)
        
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        try:
            # Проверяем и санитизируем данные в зависимости от метода
            if request.method in ['POST', 'PUT', 'PATCH']:
                await self._sanitize_request_data(request, request_id)
            
            # Проверяем query параметры
            if request.query_params:
                await self._sanitize_query_params(request, request_id)
                
        except Exception as e:
            logger.error(f"🚨 Ошибка в SecurityMiddleware: {e}")
            log_security_event(
                logger,
                "security_middleware_error",
                details={"error": str(e), "request_id": request_id},
                request=request
            )
            
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid request data"}
            )
        
        return await call_next(request)
    
    async def _sanitize_request_data(self, request: Request, request_id: str):
        """Санитизация данных тела запроса"""
        
        content_type = request.headers.get('content-type', '')
        
        if 'application/json' in content_type:
            await self._sanitize_json_data(request, request_id)
        elif 'application/x-www-form-urlencoded' in content_type:
            await self._sanitize_form_data(request, request_id)
        elif 'multipart/form-data' in content_type:
            await self._sanitize_multipart_data(request, request_id)
    
    async def _sanitize_json_data(self, request: Request, request_id: str):
        """Санитизация JSON данных"""
        
        try:
            body = await request.body()
            if not body:
                return
                
            # Парсим JSON
            try:
                data = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                logger.warning(f"🚨 Некорректный JSON в запросе: {request_id}")
                raise ValueError("Invalid JSON data")
            
            # Проверяем на атаки
            if check_for_attacks(data, request_id):
                logger.warning(f"🚨 Обнаружена атака в JSON данных: {request_id}")
                raise ValueError("Malicious content detected")
            
            # Санитизируем данные
            sanitized_data = sanitize_form_data(data, request_id)
            
            # Сохраняем санитизированные данные в request.state
            request.state.sanitized_json = sanitized_data
            
        except Exception as e:
            logger.error(f"🚨 Ошибка санитизации JSON: {e}")
            raise
    
    async def _sanitize_form_data(self, request: Request, request_id: str):
        """Санитизация form данных"""
        
        try:
            form_data = await request.form()
            if not form_data:
                return
                
            # Конвертируем в словарь
            data = {}
            for key, value in form_data.items():
                if hasattr(value, 'read'):  # Файл
                    data[key] = value  # Файлы не санитизируем
                else:
                    data[key] = str(value)
            
            # Проверяем на атаки
            if check_for_attacks(data, request_id):
                logger.warning(f"🚨 Обнаружена атака в form данных: {request_id}")
                raise ValueError("Malicious content detected")
            
            # Санитизируем данные
            sanitized_data = sanitize_form_data(data, request_id)
            
            # Сохраняем санитизированные данные в request.state
            request.state.sanitized_form = sanitized_data
            
        except Exception as e:
            logger.error(f"🚨 Ошибка санитизации form данных: {e}")
            raise
    
    async def _sanitize_multipart_data(self, request: Request, request_id: str):
        """Санитизация multipart данных"""
        
        try:
            form_data = await request.form()
            if not form_data:
                return
                
            # Конвертируем в словарь, разделяя файлы и текст
            text_data = {}
            files = {}
            
            for key, value in form_data.items():
                if hasattr(value, 'read'):  # Файл
                    files[key] = value
                else:
                    text_data[key] = str(value)
            
            # Проверяем текстовые данные на атаки
            if check_for_attacks(text_data, request_id):
                logger.warning(f"🚨 Обнаружена атака в multipart данных: {request_id}")
                raise ValueError("Malicious content detected")
            
            # Санитизируем текстовые данные
            sanitized_text = sanitize_form_data(text_data, request_id)
            
            # Сохраняем санитизированные данные в request.state
            request.state.sanitized_form = sanitized_text
            request.state.uploaded_files = files
            
        except Exception as e:
            logger.error(f"🚨 Ошибка санитизации multipart данных: {e}")
            raise
    
    async def _sanitize_query_params(self, request: Request, request_id: str):
        """Санитизация query параметров"""
        
        try:
            query_data = dict(request.query_params)
            if not query_data:
                return
                
            # Проверяем на атаки
            if check_for_attacks(query_data, request_id):
                logger.warning(f"🚨 Обнаружена атака в query параметрах: {request_id}")
                raise ValueError("Malicious content detected")
            
            # Санитизируем данные
            sanitized_query = sanitize_form_data(query_data, request_id)
            
            # Сохраняем санитизированные данные в request.state
            request.state.sanitized_query = sanitized_query
            
        except Exception as e:
            logger.error(f"🚨 Ошибка санитизации query параметров: {e}")
            raise


def get_sanitized_data(request: Request) -> dict:
    """
    Получение санитизированных данных из запроса
    """
    sanitized = {}
    
    # JSON данные
    if hasattr(request.state, 'sanitized_json'):
        sanitized.update(request.state.sanitized_json)
    
    # Form данные
    if hasattr(request.state, 'sanitized_form'):
        sanitized.update(request.state.sanitized_form)
    
    # Query параметры
    if hasattr(request.state, 'sanitized_query'):
        sanitized.update(request.state.sanitized_query)
    
    return sanitized


def get_uploaded_files(request: Request) -> dict:
    """
    Получение загруженных файлов из запроса
    """
    return getattr(request.state, 'uploaded_files', {}) 