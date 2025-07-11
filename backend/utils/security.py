import re
import html
import bleach
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse
import logging

from utils.logging_config import log_security_event

logger = logging.getLogger(__name__)


class InputSanitizer:
    """
    Класс для санитизации входных данных и защиты от XSS
    """
    
    # Разрешенные HTML теги для пользовательского контента
    ALLOWED_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'b', 'i', 
        'ul', 'ol', 'li', 'blockquote', 'a'
    ]
    
    # Разрешенные атрибуты для HTML тегов
    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title'],
        '*': ['class']
    }
    
    # Разрешенные протоколы для ссылок
    ALLOWED_PROTOCOLS = ['http', 'https', 'mailto', 'tel']
    
    # Опасные паттерны для обнаружения
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'<form[^>]*>.*?</form>',
        r'<input[^>]*>',
        r'<link[^>]*>',
        r'<meta[^>]*>',
        r'<style[^>]*>.*?</style>'
    ]
    
    def __init__(self):
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE | re.DOTALL) 
                                 for pattern in self.DANGEROUS_PATTERNS]
    
    def sanitize_html(self, content: str, request_id: str = None) -> str:
        """
        Санитизация HTML контента
        """
        if not content:
            return ""
            
        # Проверяем на опасные паттерны
        for pattern in self.compiled_patterns:
            if pattern.search(content):
                logger.warning(f"🚨 Обнаружен опасный паттерн в HTML: {pattern.pattern}")
                if request_id:
                    log_security_event(
                        "xss_attempt_detected",
                        request_id=request_id,
                        details={"pattern": pattern.pattern, "content_preview": content[:100]}
                    )
        
        # Очищаем HTML с помощью bleach
        cleaned = bleach.clean(
            content,
            tags=self.ALLOWED_TAGS,
            attributes=self.ALLOWED_ATTRIBUTES,
            protocols=self.ALLOWED_PROTOCOLS,
            strip=True
        )
        
        return cleaned
    
    def sanitize_string(self, value: str, max_length: int = 1000) -> str:
        """
        Санитизация обычной строки
        """
        if not value:
            return ""
            
        # Ограничиваем длину
        if len(value) > max_length:
            value = value[:max_length]
            
        # Экранируем HTML символы
        value = html.escape(value)
        
        # Удаляем управляющие символы
        value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', value)
        
        return value.strip()
    
    def sanitize_email(self, email: str) -> Optional[str]:
        """
        Санитизация email адреса
        """
        if not email:
            return None
            
        # Базовая проверка формата email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return None
            
        return email.lower().strip()
    
    def sanitize_phone(self, phone: str) -> Optional[str]:
        """
        Санитизация номера телефона
        """
        if not phone:
            return None
            
        # Удаляем все кроме цифр и знака +
        phone = re.sub(r'[^\d+]', '', phone)
        
        # Проверяем длину
        if len(phone) < 10 or len(phone) > 15:
            return None
            
        return phone
    
    def sanitize_url(self, url: str) -> Optional[str]:
        """
        Санитизация URL
        """
        if not url:
            return None
            
        try:
            parsed = urlparse(url)
            
            # Проверяем протокол
            if parsed.scheme not in self.ALLOWED_PROTOCOLS:
                return None
                
            # Проверяем на опасные символы
            dangerous_chars = ['<', '>', '"', "'", '`']
            if any(char in url for char in dangerous_chars):
                return None
                
            return url
            
        except Exception:
            return None
    
    def sanitize_dict(self, data: Dict[str, Any], request_id: str = None) -> Dict[str, Any]:
        """
        Санитизация словаря данных
        """
        if not isinstance(data, dict):
            return {}
            
        sanitized = {}
        
        for key, value in data.items():
            # Санитизируем ключ
            clean_key = self.sanitize_string(str(key), max_length=100)
            
            # Санитизируем значение в зависимости от типа
            if isinstance(value, str):
                if 'email' in key.lower():
                    clean_value = self.sanitize_email(value)
                elif 'phone' in key.lower() or 'tel' in key.lower():
                    clean_value = self.sanitize_phone(value)
                elif 'url' in key.lower() or 'link' in key.lower():
                    clean_value = self.sanitize_url(value)
                elif 'html' in key.lower() or 'content' in key.lower():
                    clean_value = self.sanitize_html(value, request_id)
                else:
                    clean_value = self.sanitize_string(value)
            elif isinstance(value, (int, float)):
                clean_value = value
            elif isinstance(value, bool):
                clean_value = value
            elif isinstance(value, list):
                clean_value = [self.sanitize_string(str(item)) for item in value if item is not None]
            elif isinstance(value, dict):
                clean_value = self.sanitize_dict(value, request_id)
            else:
                clean_value = self.sanitize_string(str(value))
            
            if clean_value is not None:
                sanitized[clean_key] = clean_value
                
        return sanitized


class SQLInjectionProtector:
    """
    Защита от SQL инъекций
    """
    
    # Опасные SQL ключевые слова
    DANGEROUS_SQL_KEYWORDS = [
        'union', 'select', 'insert', 'update', 'delete', 'drop', 'create',
        'alter', 'exec', 'execute', 'sp_', 'xp_', 'script', 'declare',
        'cast', 'convert', 'char', 'varchar', 'nchar', 'nvarchar'
    ]
    
    # Опасные символы для SQL
    DANGEROUS_SQL_CHARS = [';', '--', '/*', '*/', 'xp_', 'sp_']
    
    def __init__(self):
        self.sql_pattern = re.compile(
            r'\b(' + '|'.join(self.DANGEROUS_SQL_KEYWORDS) + r')\b',
            re.IGNORECASE
        )
    
    def check_sql_injection(self, value: str, request_id: str = None) -> bool:
        """
        Проверка на SQL инъекции
        """
        if not value:
            return False
            
        # Проверяем на опасные ключевые слова
        if self.sql_pattern.search(value):
            logger.warning(f"🚨 Обнаружена попытка SQL инъекции: {value[:100]}")
            if request_id:
                log_security_event(
                    "sql_injection_attempt",
                    request_id=request_id,
                    details={"content_preview": value[:100]}
                )
            return True
            
        # Проверяем на опасные символы
        for char_seq in self.DANGEROUS_SQL_CHARS:
            if char_seq in value:
                logger.warning(f"🚨 Обнаружены опасные SQL символы: {char_seq}")
                if request_id:
                    log_security_event(
                        "sql_injection_attempt",
                        request_id=request_id,
                        details={"dangerous_chars": char_seq, "content_preview": value[:100]}
                    )
                return True
                
        return False


# Глобальные экземпляры
input_sanitizer = InputSanitizer()
sql_protector = SQLInjectionProtector()


def sanitize_form_data(form_data: Dict[str, Any], request_id: str = None) -> Dict[str, Any]:
    """
    Санитизация данных формы
    """
    return input_sanitizer.sanitize_dict(form_data, request_id)


def check_for_attacks(data: Union[str, Dict[str, Any]], request_id: str = None) -> bool:
    """
    Проверка данных на атаки
    """
    if isinstance(data, str):
        return sql_protector.check_sql_injection(data, request_id)
    elif isinstance(data, dict):
        for value in data.values():
            if isinstance(value, str) and sql_protector.check_sql_injection(value, request_id):
                return True
    return False 