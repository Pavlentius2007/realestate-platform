"""
Конфигурация интернационализации
"""

SUPPORTED_LANGUAGES = {
    'ru': {
        'name': 'Russian',
        'native': 'Русский',
        'fallback': 'en'
    },
    'en': {
        'name': 'English',
        'native': 'English',
        'fallback': None
    },
    'th': {
        'name': 'Thai',
        'native': 'ไทย',
        'fallback': 'en'
    },
    'zh': {
        'name': 'Chinese',
        'native': '中文',
        'fallback': 'en'
    }
}

DEFAULT_LANGUAGE = 'en'

# Настройки сессии и cookie
LANGUAGE_COOKIE_NAME = 'lang'
LANGUAGE_COOKIE_MAX_AGE = 31536000  # 1 год
LANGUAGE_SESSION_KEY = 'lang'

# Приоритеты определения языка
LANGUAGE_DETECTION_ORDER = [
    'url',      # Первый приоритет - язык из URL
    'session',  # Второй приоритет - язык из сессии
    'cookie',   # Третий приоритет - язык из cookie
    'header'    # Четвертый приоритет - язык из Accept-Language
]

# Настройки кэширования
TRANSLATIONS_CACHE_SIZE = 10000  # Размер кэша переводов
TRANSLATIONS_CACHE_TTL = 3600   # Время жизни кэша в секундах

# Настройки логирования
TRANSLATION_DEBUG = True  # Включает подробное логирование переводов
TRANSLATION_LOG_MISSING = True  # Логировать отсутствующие переводы

# Пути к файлам переводов
TRANSLATIONS_DIR = 'locales'  # Относительно корня проекта
TRANSLATIONS_FORMAT = 'json'  # Формат файлов переводов 