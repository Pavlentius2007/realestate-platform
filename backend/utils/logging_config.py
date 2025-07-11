import logging
import logging.handlers
from pathlib import Path
import os
from datetime import datetime
import json


class CustomJSONFormatter(logging.Formatter):
    """
    Кастомный JSON форматтер для структурированного логирования
    """
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Добавляем дополнительные поля если есть
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'ip_address'):
            log_entry['ip_address'] = record.ip_address
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'endpoint'):
            log_entry['endpoint'] = record.endpoint
        if hasattr(record, 'method'):
            log_entry['method'] = record.method
        if hasattr(record, 'status_code'):
            log_entry['status_code'] = record.status_code
        if hasattr(record, 'response_time'):
            log_entry['response_time'] = record.response_time
            
        # Добавляем информацию об исключении если есть
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry, ensure_ascii=False, separators=(',', ':'))


class SecurityFilter(logging.Filter):
    """
    Фильтр для логирования событий безопасности
    """
    
    def filter(self, record):
        # Логируем только события безопасности
        security_keywords = [
            'authentication', 'authorization', 'csrf', 'rate_limit', 
            'login', 'logout', 'register', 'token', 'suspicious',
            'blocked', 'failed', 'unauthorized', 'forbidden'
        ]
        
        message = record.getMessage().lower()
        return any(keyword in message for keyword in security_keywords)


class PerformanceFilter(logging.Filter):
    """
    Фильтр для логирования событий производительности
    """
    
    def filter(self, record):
        # Логируем события производительности
        return (
            hasattr(record, 'response_time') or
            'performance' in record.getMessage().lower() or
            'slow' in record.getMessage().lower() or
            'timeout' in record.getMessage().lower()
        )


def setup_logging(config_name: str = "production"):
    """
    Настройка централизованного логирования
    
    Args:
        config_name: Конфигурация логирования (development, production, testing)
    """
    
    # Создаем директорию для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Получаем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Очищаем существующие handlers
    root_logger.handlers.clear()
    
    # Создаем форматтеры
    json_formatter = CustomJSONFormatter()
    
    # Консольный форматтер для разработки
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # === КОНСОЛЬНЫЙ HANDLER ===
    console_handler = logging.StreamHandler()
    if config_name == "development":
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(console_formatter)
    else:
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(json_formatter)
    
    root_logger.addHandler(console_handler)
    
    # === ОСНОВНОЙ ФАЙЛ ЛОГОВ ===
    main_handler = logging.handlers.RotatingFileHandler(
        log_dir / "sianoro.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    main_handler.setLevel(logging.INFO)
    main_handler.setFormatter(json_formatter)
    root_logger.addHandler(main_handler)
    
    # === ФАЙЛ ЛОГОВ ОШИБОК ===
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / "errors.log",
        maxBytes=10*1024*1024,
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)
    root_logger.addHandler(error_handler)
    
    # === ФАЙЛ ЛОГОВ БЕЗОПАСНОСТИ ===
    security_handler = logging.handlers.RotatingFileHandler(
        log_dir / "security.log",
        maxBytes=10*1024*1024,
        backupCount=30,  # Храним дольше для аудита
        encoding='utf-8'
    )
    security_handler.setLevel(logging.INFO)
    security_handler.setFormatter(json_formatter)
    security_handler.addFilter(SecurityFilter())
    root_logger.addHandler(security_handler)
    
    # === ФАЙЛ ЛОГОВ ПРОИЗВОДИТЕЛЬНОСТИ ===
    performance_handler = logging.handlers.RotatingFileHandler(
        log_dir / "performance.log",
        maxBytes=10*1024*1024,
        backupCount=7,
        encoding='utf-8'
    )
    performance_handler.setLevel(logging.INFO)
    performance_handler.setFormatter(json_formatter)
    performance_handler.addFilter(PerformanceFilter())
    root_logger.addHandler(performance_handler)
    
    # === ФАЙЛ ЛОГОВ ДОСТУПА ===
    access_handler = logging.handlers.RotatingFileHandler(
        log_dir / "access.log",
        maxBytes=10*1024*1024,
        backupCount=7,
        encoding='utf-8'
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(json_formatter)
    
    # Создаем отдельный логгер для доступа
    access_logger = logging.getLogger("access")
    access_logger.setLevel(logging.INFO)
    access_logger.addHandler(access_handler)
    access_logger.propagate = False  # Не передаем в root logger
    
    # === НАСТРОЙКА ЛОГГЕРОВ БИБЛИОТЕК ===
    
    # Uvicorn
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.INFO)
    
    # FastAPI
    fastapi_logger = logging.getLogger("fastapi")
    fastapi_logger.setLevel(logging.INFO)
    
    # SQLAlchemy - только ошибки
    sqlalchemy_logger = logging.getLogger("sqlalchemy")
    sqlalchemy_logger.setLevel(logging.WARNING)
    
    # Отключаем verbose логирование для некоторых библиотек
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.WARNING)
    
    # Логируем запуск системы логирования
    logger = logging.getLogger(__name__)
    logger.info(f"🔧 Система логирования настроена ({config_name})")
    logger.info(f"📁 Логи сохраняются в: {log_dir.absolute()}")
    
    return logger


def get_logger(name: str = None):
    """
    Получить настроенный логгер
    
    Args:
        name: Имя логгера (по умолчанию - имя модуля)
    
    Returns:
        logging.Logger: Настроенный логгер
    """
    return logging.getLogger(name or __name__)


def log_request(logger: logging.Logger, request, response=None, start_time=None):
    """
    Логирование HTTP запроса
    
    Args:
        logger: Логгер для записи
        request: FastAPI Request объект
        response: FastAPI Response объект (опционально)
        start_time: Время начала запроса для расчета времени выполнения
    """
    import time
    
    # Получаем IP адрес
    ip_address = request.client.host if request.client else "unknown"
    
    # Получаем информацию о пользователе если доступна
    user_id = getattr(request.state, 'user_id', None)
    
    # Рассчитываем время выполнения
    response_time = None
    if start_time:
        response_time = round((time.time() - start_time) * 1000, 2)  # в миллисекундах
    
    # Статус код
    status_code = response.status_code if response else None
    
    # Создаем запись лога
    extra = {
        'ip_address': ip_address,
        'method': request.method,
        'endpoint': str(request.url),
        'user_agent': request.headers.get('user-agent', ''),
        'referer': request.headers.get('referer', ''),
    }
    
    if user_id:
        extra['user_id'] = user_id
    if status_code:
        extra['status_code'] = status_code
    if response_time:
        extra['response_time'] = response_time
    
    # Определяем уровень логирования
    if status_code and status_code >= 500:
        level = logging.ERROR
    elif status_code and status_code >= 400:
        level = logging.WARNING
    else:
        level = logging.INFO
    
    message = f"{request.method} {request.url.path}"
    if status_code:
        message += f" -> {status_code}"
    if response_time:
        message += f" ({response_time}ms)"
    
    logger.log(level, message, extra=extra)


def log_security_event(logger: logging.Logger, event_type: str, details: dict, request=None):
    """
    Логирование событий безопасности
    
    Args:
        logger: Логгер для записи
        event_type: Тип события (login, logout, csrf_violation, rate_limit_exceeded, etc.)
        details: Детали события
        request: FastAPI Request объект (опционально)
    """
    
    extra = {
        'event_type': event_type,
        **details
    }
    
    if request:
        extra['ip_address'] = request.client.host if request.client else "unknown"
        extra['user_agent'] = request.headers.get('user-agent', '')
        extra['endpoint'] = str(request.url)
    
    logger.warning(f"Security event: {event_type}", extra=extra)


def log_performance_event(logger: logging.Logger, operation: str, duration: float, details: dict = None):
    """
    Логирование событий производительности
    
    Args:
        logger: Логгер для записи
        operation: Название операции
        duration: Длительность в секундах
        details: Дополнительные детали
    """
    
    extra = {
        'operation': operation,
        'duration': duration,
        'response_time': round(duration * 1000, 2)  # в миллисекундах
    }
    
    if details:
        extra.update(details)
    
    # Определяем уровень на основе длительности
    if duration > 5.0:  # Более 5 секунд
        level = logging.ERROR
    elif duration > 1.0:  # Более 1 секунды
        level = logging.WARNING
    else:
        level = logging.INFO
    
    logger.log(level, f"Performance: {operation} took {duration:.2f}s", extra=extra) 