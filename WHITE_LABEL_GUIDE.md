# 🎨 White Label Guide - Руководство по кастомизации

Это руководство поможет вам настроить платформу недвижимости под ваши нужды для продажи как white label решение.

## 📋 Содержание

1. [Быстрый старт](#быстрый-старт)
2. [Конфигурация брендинга](#конфигурация-брендинга)
3. [Настройка контактов](#настройка-контактов)
4. [Управление функциями](#управление-функциями)
5. [Кастомизация стилей](#кастомизация-стилей)
6. [SEO настройки](#seo-настройки)
7. [Аналитика](#аналитика)
8. [Развертывание](#развертывание)

## 🚀 Быстрый старт

### 1. Клонирование и настройка

```bash
# Клонируйте репозиторий
git clone <your-repo-url>
cd realestate-platform

# Скопируйте файл конфигурации
cp config.env.example .env

# Отредактируйте .env файл под ваши нужды
nano .env
```

### 2. Установка зависимостей

```bash
# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установите зависимости
pip install -r requirements.txt
```

### 3. Запуск

```bash
python run_server.py
```

## 🎨 Конфигурация брендинга

### Основные настройки

В файле `.env` настройте:

```env
# Название компании
BRAND_NAME=Your Company Name

# Слоган
BRAND_TAGLINE=Ваш надежный партнер в сфере недвижимости

# Цвета бренда
PRIMARY_COLOR=#0074E4
SECONDARY_COLOR=#005bb5
ACCENT_COLOR=#3b82f6
```

### Логотип и иконки

Замените файлы в папке `static/img/`:
- `sianoro-logo.png` - ваш логотип
- `favicon.ico` - иконка сайта
- `og-image.jpg` - изображение для соцсетей

### Программная настройка

В файле `backend/config/settings.py` можно изменить:

```python
@dataclass
class BrandConfig:
    name: str = "Your Company"
    tagline: str = "Your tagline"
    logo_url: str = "/static/img/your-logo.png"
    primary_color: str = "#your-color"
```

## 📞 Настройка контактов

### Контактная информация

```env
# Телефон
CONTACT_PHONE=+66 95 386 2858

# WhatsApp
CONTACT_WHATSAPP=+66 95 386 2858

# Telegram
CONTACT_TELEGRAM=t.me/YourChannel

# Email
CONTACT_EMAIL=info@yourcompany.com

# Адрес
CONTACT_ADDRESS=Ваш адрес
```

### Социальные сети

В `backend/config/settings.py`:

```python
@dataclass
class ContactConfig:
    instagram: str = "your-instagram"
    facebook: str = "your-facebook"
    youtube: str = "your-youtube"
    linkedin: str = "your-linkedin"
```

## ⚙️ Управление функциями

### Включение/отключение функций

```env
# Калькулятор инвестиций
ENABLE_CALCULATOR=true

# ИИ-ассистент
ENABLE_AI_ASSISTANT=true

# Избранное
ENABLE_FAVORITES=true

# Статьи
ENABLE_ARTICLES=true

# Проекты
ENABLE_PROJECTS=true

# Аренда
ENABLE_RENTAL=true
```

### Программное управление

В шаблонах используйте:

```html
{% if config.features.enable_calculator %}
  <!-- Калькулятор -->
{% endif %}

{% if config.features.enable_ai_assistant %}
  <!-- ИИ-ассистент -->
{% endif %}
```

## 🎨 Кастомизация стилей

### Темы

В `backend/config/themes.py` создайте новую тему:

```python
def _get_custom_theme(self) -> Dict[str, Any]:
    return {
        "colors": {
            "primary": "#your-color",
            "secondary": "#your-color",
            # ... другие цвета
        },
        "gradients": {
            "primary": "linear-gradient(135deg, #your-color 0%, #your-color 100%)",
            # ... другие градиенты
        }
    }
```

### CSS переменные

Все цвета и стили доступны как CSS переменные:

```css
:root {
    --color-primary: #0074E4;
    --color-secondary: #005bb5;
    --gradient-primary: linear-gradient(135deg, #0074E4 0%, #005bb5 100%);
    --spacing-md: 1rem;
    --radius-md: 0.5rem;
}
```

### Кастомные стили

Создайте файл `static/css/custom.css`:

```css
/* Ваши кастомные стили */
.btn-primary {
    background: var(--gradient-primary);
    color: white;
}

.hero-section {
    background: var(--gradient-hero);
}
```

## 🔍 SEO настройки

### Мета-теги

```env
# Заголовок сайта
SITE_TITLE=Your Company - Недвижимость в Таиланде

# Описание
SITE_DESCRIPTION=Найдите идеальную недвижимость для жизни и инвестиций

# Ключевые слова
SITE_KEYWORDS=недвижимость, таиланд, квартиры, инвестиции
```

### Open Graph

```env
# Изображение для соцсетей
OG_IMAGE=/static/img/og-image.jpg

# Тип контента
OG_TYPE=website
```

## 📊 Аналитика

### Google Analytics

```env
GOOGLE_ANALYTICS_ID=GA_MEASUREMENT_ID
```

### Yandex Metrika

```env
YANDEX_METRIKA_ID=YOUR_METRIKA_ID
```

### Facebook Pixel

```env
FACEBOOK_PIXEL_ID=YOUR_PIXEL_ID
```

## 🌐 Локализация

### Поддерживаемые языки

В `backend/config/settings.py`:

```python
@dataclass
class LocalizationConfig:
    default_language: str = "ru"
    supported_languages: List[str] = ["ru", "en", "th", "zh"]
```

### Переводы

Добавьте переводы в папку `locales/`:

```json
// locales/your-lang.json
{
  "navigation": {
    "buy_property": "Купить",
    "rent_property": "Снять"
  }
}
```

## 💰 Платежи

### Настройка валюты

```env
# Валюта
CURRENCY=THB

# Символ валюты
CURRENCY_SYMBOL=฿

# Включить платежи
ENABLE_PAYMENTS=false
```

## 🚀 Развертывание

### Продакшн настройки

1. **Создайте файл `.env.production`**:

```env
# Продакшн настройки
DEBUG=false
SECRET_KEY=your-super-secure-production-key
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

2. **Настройте веб-сервер** (Nginx + Gunicorn):

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /path/to/your/static/;
    }
}
```

3. **Запуск с Gunicorn**:

```bash
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8002
```

### Docker развертывание

Создайте `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8002

CMD ["gunicorn", "backend.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8002"]
```

## 📦 Структура проекта для white label

```
realestate-platform/
├── backend/
│   ├── config/
│   │   ├── settings.py      # Основные настройки
│   │   ├── themes.py        # Система тем
│   │   └── __init__.py
│   ├── utils/
│   │   └── config_utils.py  # Утилиты конфигурации
│   └── templates/
│       └── base.html        # Базовый шаблон
├── static/
│   ├── img/                 # Изображения бренда
│   └── css/                 # Стили
├── locales/                 # Переводы
├── config.env.example       # Пример конфигурации
└── WHITE_LABEL_GUIDE.md     # Это руководство
```

## 🔧 Продвинутая кастомизация

### Создание собственной темы

1. Создайте новый класс темы в `backend/config/themes.py`
2. Добавьте тему в `ThemeManager`
3. Установите тему через `theme_manager.set_theme("your-theme")`

### Кастомные компоненты

Создайте компоненты в `backend/templates/components/`:

```html
<!-- components/custom-header.html -->
<header class="custom-header">
    <h1>{{ config.brand.name }}</h1>
    <p>{{ config.brand.tagline }}</p>
</header>
```

### API кастомизация

Добавьте кастомные эндпоинты в `backend/routers/`:

```python
# routers/custom.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/custom-endpoint")
async def custom_endpoint():
    return {"message": "Custom functionality"}
```

## 📞 Поддержка

Для получения поддержки:
- Создайте issue в репозитории
- Обратитесь к документации
- Проверьте примеры в папке `examples/`

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для подробностей.

---

**Удачной кастомизации! 🎉** 