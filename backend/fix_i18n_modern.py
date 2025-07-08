"""
🌍 Современная система переводов для FastAPI на основе JSON
Полная замена gettext для лучшей производительности
"""

import json
import os
from pathlib import Path
from fastapi import Request
from typing import Dict, Any, Optional
import threading
import time
from collections import OrderedDict
from backend.config.i18n import (
    SUPPORTED_LANGUAGES,
    DEFAULT_LANGUAGE,
    LANGUAGE_COOKIE_NAME,
    LANGUAGE_COOKIE_MAX_AGE,
    LANGUAGE_SESSION_KEY,
    LANGUAGE_DETECTION_ORDER
)

# Определяем корневую директорию проекта независимо от рабочей директории
CURRENT_FILE = Path(__file__).resolve()
if CURRENT_FILE.parent.name == "backend":
    # Запуск из backend директории или файл находится в backend
    BASE_DIR = CURRENT_FILE.parent.parent  # realestate-platform
else:
    # Запуск из корневой директории
    BASE_DIR = CURRENT_FILE.parent  # realestate-platform

# Проверяем что locales директория существует
LOCALES_DIR = BASE_DIR / "locales"
if not LOCALES_DIR.exists():
    print(f"⚠️ Директория переводов не найдена: {LOCALES_DIR}")
    print(f"📁 Создаю директорию: {LOCALES_DIR}")
    LOCALES_DIR.mkdir(exist_ok=True)

class LRUCache:
    """Кэш с ограниченным размером и временем жизни записей"""
    def __init__(self, capacity: int = 1000, ttl: int = 3600):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.ttl = ttl
        self.timestamps = {}
        self._lock = threading.Lock()
        
    def get(self, key: str) -> Optional[str]:
        with self._lock:
            if key not in self.cache:
                return None
            
            # Проверяем TTL
            if time.time() - self.timestamps[key] > self.ttl:
                del self.cache[key]
                del self.timestamps[key]
                return None
                
            # Обновляем позицию в LRU
            self.cache.move_to_end(key)
            return self.cache[key]
        
    def put(self, key: str, value: str):
        with self._lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            self.timestamps[key] = time.time()
            
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)
                
    def clear(self):
        with self._lock:
            self.cache.clear()
            self.timestamps.clear()
        
    def __contains__(self, key: str) -> bool:
        """Поддержка оператора in"""
        with self._lock:
            return key in self.cache and time.time() - self.timestamps[key] <= self.ttl

class ModernI18n:
    """Современная система переводов на основе JSON"""
    
    def __init__(self):
        self.translations: Dict[str, Dict[str, str]] = {}
        self.cache = LRUCache(capacity=10000, ttl=3600)
        self._lock = threading.Lock()
        self.load_translations()
        
    def load_translations(self):
        """Загружает переводы из JSON файлов"""
        self.cache.clear()
        print("🧹 Кэш очищен")
        print(f"🔍 Поиск переводов в: {LOCALES_DIR}")
        with self._lock:
            for lang in SUPPORTED_LANGUAGES:
                json_file = LOCALES_DIR / f"{lang}.json"
                try:
                    if json_file.exists():
                        with open(json_file, 'r', encoding='utf-8') as f:
                            translations = json.load(f)
                            self.translations[lang] = translations
                            print(f"✅ Загружены переводы для языка {lang}")
                    else:
                        print(f"⚠️ Файл переводов не найден: {json_file}")
                except Exception as e:
                    print(f"❌ Ошибка загрузки переводов для {lang}: {e}")
            if not any(self.translations.values()):
                print("❌ ВНИМАНИЕ: Не загружено ни одного перевода!")
                print(f"📁 Проверьте наличие файлов .json в директории: {LOCALES_DIR}")
            else:
                print(f"📊 Загружено языков: {list(self.translations.keys())}")
    
    def parse_accept_language(self, header: str):
        """
        Парсит Accept-Language и возвращает список языков по приоритету (с учетом q-values)
        """
        langs = []
        if not header:
            return []
        parts = [h.strip() for h in header.split(',') if h.strip()]
        for part in parts:
            if ';' in part:
                lang, qval = part.split(';', 1)
                try:
                    q = float(qval.split('=')[1])
                except Exception:
                    q = 1.0
            else:
                lang = part
                q = 1.0
            lang = lang.lower().replace('_', '-')
            langs.append((q, lang))
            # Добавляем базовый язык с чуть меньшим приоритетом
            if '-' in lang:
                base = lang.split('-')[0]
                langs.append((q - 0.001, base))
        langs.sort(reverse=True)
        return [l[1] for l in langs]

    def get_user_language(self, request: Request) -> str:
        """Определяет язык пользователя по приоритетам из конфигурации"""
        for priority in LANGUAGE_DETECTION_ORDER:
            if priority == 'url':
                path = str(request.url.path)
                if path.startswith('/'):
                    parts = path.strip('/').split('/')
                    if parts and parts[0] in SUPPORTED_LANGUAGES:
                        print(f"🌍 Язык из URL: {parts[0]}")
                        return parts[0]
            elif priority == 'session':
                try:
                    if hasattr(request, 'session') and request.session:
                        session_lang = request.session.get(LANGUAGE_SESSION_KEY)
                        if session_lang and session_lang in SUPPORTED_LANGUAGES:
                            print(f"🌍 Язык из сессии: {session_lang}")
                            return session_lang
                except Exception as e:
                    print(f"🌍 Ошибка получения языка из сессии: {e}")
            elif priority == 'cookie':
                try:
                    cookie_lang = request.cookies.get(LANGUAGE_COOKIE_NAME)
                    if cookie_lang and cookie_lang in SUPPORTED_LANGUAGES:
                        print(f"🌍 Язык из cookie: {cookie_lang}")
                        return cookie_lang
                except Exception as e:
                    print(f"🌍 Ошибка получения языка из cookie: {e}")
            elif priority == 'header':
                try:
                    accept_lang = request.headers.get("accept-language", "")
                    for code in self.parse_accept_language(accept_lang):
                        if code in SUPPORTED_LANGUAGES:
                            print(f"🌍 Язык из заголовка: {code}")
                            return code
                except Exception as e:
                    print(f"🌍 Ошибка получения языка из заголовка: {e}")
        print(f"🌍 Используем язык по умолчанию: {DEFAULT_LANGUAGE}")
        return DEFAULT_LANGUAGE
    
    def translate(self, key: str, lang: str, **kwargs) -> str:
        """
        Переводит ключ на указанный язык
        Поддерживает форматирование с параметрами и вложенные ключи
        """
        # Проверяем кэш
        cache_key = f"{lang}:{key}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached.format(**kwargs) if kwargs else cached
            
        # Если перевода нет в кэше, ищем в словаре
        translation = None
        
        def get_nested_value(data: dict, nested_key: str):
            """Получает значение по вложенному ключу (например, 'site.title')"""
            keys = nested_key.split('.')
            current = data
            for k in keys:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    return None
            return current if not isinstance(current, dict) else None

        # Сначала пробуем прямой перевод
        if lang in self.translations:
            translation = get_nested_value(self.translations[lang], key)
            
        # Если это обычный текст (не ключ), возвращаем его как есть
        if translation is None and key not in ['lang', 'request'] and not key.startswith('_'):
            translation = key
            
        # Если перевод не найден, пробуем английский
        if translation is None and lang != 'en' and 'en' in self.translations:
            translation = get_nested_value(self.translations['en'], key)
            if translation:
                print(f"⚠️ Используем английский перевод для {key} (язык: {lang})")
        
        if translation:
            # Кэшируем результат
            self.cache.put(cache_key, translation)
            # Возвращаем с форматированием если есть параметры
            return translation.format(**kwargs) if kwargs else translation
            
        # Если перевод не найден, возвращаем ключ
        print(f"❌ Перевод не найден: {key} (язык: {lang})")
        return key

# Создаем глобальный экземпляр
i18n = ModernI18n()

def reload_translations():
    """Перезагрузка переводов в runtime"""
    i18n.load_translations()
    print("🔄 Переводы перезагружены!")

def create_translator(request: Request):
    """Создает функцию-переводчик для запроса"""
    lang = i18n.get_user_language(request)
    
    def _(key: str, **kwargs) -> str:
        result = i18n.translate(key, lang, **kwargs)
        # Если перевод не найден, попробуем прямой текст
        if result == key and key not in ['lang', 'request']:
            # Это обычный текст, не ключ перевода
            return key
        return result
    
    return _, lang


# Middleware для автоматического внедрения переводчика
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi.templating import Jinja2Templates
from starlette.responses import Response

class ModernI18nMiddleware(BaseHTTPMiddleware):
    """Единый middleware для работы с языками"""
    
    def __init__(self, app, templates: Optional[Jinja2Templates] = None):
        super().__init__(app)
        self.templates = templates
        
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Определяем язык
        try:
            # Пропускаем статические файлы, API запросы и маршрут смены языка
            path = request.url.path
            if (path.startswith("/static/") or 
                path.startswith("/api/") or 
                path.startswith("/admin") or
                path.startswith("/favicon.ico") or
                path.startswith("/robots.txt") or
                path.startswith("/lang/")):
                response = await call_next(request)
                return response

            lang = i18n.get_user_language(request)
            
            # Создаем функцию перевода
            def _(key: str, **kwargs) -> str:
                return i18n.translate(key, lang, **kwargs)
                
            # Добавляем в scope запроса
            request.scope["_"] = _
            request.scope["translate"] = _
            request.scope["lang"] = lang
            
            # Добавляем в шаблоны
            if self.templates:
                # Импортируем функции конфигурации
                try:
                    from backend.utils.config_utils import get_config_for_template, get_analytics_scripts
                except ImportError:
                    try:
                        from utils.config_utils import get_config_for_template, get_analytics_scripts
                    except ImportError:
                        # Fallback если конфигурация недоступна
                        def get_config_for_template():
                            return {"seo": {"site_title": "Sianoro"}}
                        def get_analytics_scripts() -> str:
                            return ""
                
                # Получаем конфигурацию
                config = get_config_for_template()
                analytics_scripts = get_analytics_scripts()
                
                self.templates.env.globals.update({
                    "_": _,
                    "translate": _,
                    "lang": lang,
                    "supported_languages": SUPPORTED_LANGUAGES,
                    "config": config,
                    "analytics_scripts": analytics_scripts
                })
                
            # Дополнительно обновляем шаблоны, используемые админкой
            try:
                from backend.config.templates import templates as admin_templates
                # Убеждаемся что config и analytics_scripts определены
                if 'config' not in locals():
                    try:
                        from backend.utils.config_utils import get_config_for_template, get_analytics_scripts
                    except ImportError:
                        def get_config_for_template():
                            return {"seo": {"site_title": "Sianoro"}}
                        def get_analytics_scripts() -> str:
                            return ""
                    config = get_config_for_template()
                    analytics_scripts = get_analytics_scripts()
                
                admin_templates.env.globals.update({
                    "_": _,
                    "translate": _,
                    "lang": lang,
                    "supported_languages": SUPPORTED_LANGUAGES,
                    "config": config,
                    "analytics_scripts": analytics_scripts
                })
            except Exception as e:
                print(f"⚠️ Ошибка обновления админских шаблонов: {e}")
                pass
                
            # Проверяем URL и редиректим если нужно
            path_parts = path.strip('/').split('/')

            # НЕ делаем редирект для маршрута смены языка
            if path.startswith('/lang/'):
                response = await call_next(request)
                return response

            if not path_parts or path_parts[0] not in SUPPORTED_LANGUAGES:
                from starlette.responses import RedirectResponse
                return RedirectResponse(f"/{lang}{path}", status_code=302)
                
            response = await call_next(request)
            return response
            
        except Exception as e:
            print(f"❌ Ошибка в ModernI18nMiddleware: {e}")
            # В случае ошибки, пропускаем запрос дальше
            return await call_next(request)


def inject_translator_to_templates(templates: Jinja2Templates, request: Request):
    """Принудительная инжекция переводчика в шаблоны (дополнительная страховка)"""
    if not hasattr(request.state, '_') or not hasattr(request.state, 'lang'):
        # Если переводчик отсутствует, создаем его
        lang = request.path_params.get('lang', 'ru')
        request.state.lang = lang
        
        def _(key: str, **kwargs) -> str:
            result = i18n.translate(key, lang, **kwargs)
            print(f"🔤 Перевод (инжекция): {key} -> {result} (язык: {lang})")
            return result
            
        request.state._ = _
    
    # Импортируем функции конфигурации
    try:
        from backend.utils.config_utils import get_config_for_template, get_analytics_scripts
    except ImportError:
        try:
            from utils.config_utils import get_config_for_template, get_analytics_scripts
        except ImportError:
            # Fallback если конфигурация недоступна
            def get_config_for_template():
                return {"seo": {"site_title": "Sianoro"}}
            def get_analytics_scripts() -> str:
                return ""
    
    # Получаем конфигурацию
    config = get_config_for_template()
    analytics_scripts = get_analytics_scripts()
    
    # Обновляем глобальные переменные шаблонов
    templates.env.globals.update({
        "_": request.state._,
        "lang": request.state.lang,
        "translate": request.state._,
        "config": config,
        "analytics_scripts": analytics_scripts
    })
    return True 