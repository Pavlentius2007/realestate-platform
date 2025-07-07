# 🏠 Sianoro - White Label Real Estate Platform

Современная платформа недвижимости с полной поддержкой white label решения. Идеально подходит для агентств недвижимости, которые хотят создать собственный сайт с уникальным брендингом.

## ✨ Особенности

### 🎨 White Label Ready
- **Полная кастомизация брендинга** - логотип, цвета, шрифты
- **Конфигурируемые контакты** - телефон, WhatsApp, Telegram, email
- **Система тем** - готовые темы + возможность создания собственных
- **Управление функциями** - включение/отключение модулей

### 🏗️ Функциональность
- **Каталог недвижимости** - покупка и аренда
- **Новостройки** - проекты на стадии строительства
- **Инвестиционный калькулятор** - расчет доходности
- **ИИ-ассистент** - умный подбор недвижимости
- **Избранное** - сохранение понравившихся объектов
- **Статьи и блог** - полезная информация для клиентов
- **Многоязычность** - русский, английский, тайский, китайский

### 🛠️ Технологии
- **Backend**: FastAPI, SQLAlchemy, SQLite/PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript, Tailwind CSS
- **Карты**: Leaflet.js
- **Аналитика**: Google Analytics, Yandex Metrika, Facebook Pixel

## 🚀 Быстрый старт

### 1. Клонирование
```bash
git clone <repository-url>
cd realestate-platform
```

### 2. Настройка white label
```bash
# Запустите скрипт настройки
python setup_white_label.py

# Или настройте вручную
cp config.env.example .env
# Отредактируйте .env файл
```

### 3. Установка зависимостей
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 4. Запуск
```bash
python run_server.py
```

Откройте http://localhost:8002/ru

## 🎨 Кастомизация

### Брендинг
Замените файлы в `static/img/brand/`:
- `logo.png` - ваш логотип
- `favicon.ico` - иконка сайта
- `og-image.jpg` - изображение для соцсетей

### Конфигурация
Отредактируйте `.env` файл:
```env
# Брендинг
BRAND_NAME=Your Company
BRAND_TAGLINE=Your tagline
PRIMARY_COLOR=#your-color

# Контакты
CONTACT_PHONE=+your-phone
CONTACT_WHATSAPP=+your-whatsapp
CONTACT_TELEGRAM=t.me/your-channel
CONTACT_EMAIL=info@yourcompany.com

# Функции
ENABLE_CALCULATOR=true
ENABLE_AI_ASSISTANT=true
```

### Темы
Создайте кастомную тему в `backend/config/themes.py`:
```python
def _get_custom_theme(self) -> Dict[str, Any]:
    return {
        "colors": {
            "primary": "#your-color",
            "secondary": "#your-color",
        },
        "gradients": {
            "primary": "linear-gradient(135deg, #your-color 0%, #your-color 100%)",
        }
    }
```

## 📁 Структура проекта

```
realestate-platform/
├── backend/
│   ├── config/              # Конфигурация
│   │   ├── settings.py      # Основные настройки
│   │   ├── themes.py        # Система тем
│   │   └── i18n.py          # Локализация
│   ├── models/              # Модели данных
│   ├── routers/             # API маршруты
│   ├── templates/           # HTML шаблоны
│   └── utils/               # Утилиты
├── static/
│   ├── css/                 # Стили
│   ├── js/                  # Скрипты
│   ├── img/                 # Изображения
│   └── locales/             # Переводы
├── locales/                 # Файлы переводов
├── config.env.example       # Пример конфигурации
├── setup_white_label.py     # Скрипт настройки
└── WHITE_LABEL_GUIDE.md     # Подробное руководство
```

## 🔧 Конфигурация

### Основные настройки
Все настройки находятся в файле `.env`:

```env
# Брендинг
BRAND_NAME=Your Company
BRAND_TAGLINE=Your tagline
PRIMARY_COLOR=#your-color

# Контакты
CONTACT_PHONE=+your-phone
CONTACT_WHATSAPP=+your-whatsapp
CONTACT_TELEGRAM=t.me/your-channel
CONTACT_EMAIL=info@yourcompany.com

# Функции
ENABLE_CALCULATOR=true
ENABLE_AI_ASSISTANT=true
ENABLE_FAVORITES=true
ENABLE_ARTICLES=true

# Аналитика
GOOGLE_ANALYTICS_ID=your-ga-id
YANDEX_METRIKA_ID=your-metrika-id
FACEBOOK_PIXEL_ID=your-pixel-id
```

### Продвинутые настройки
Для более детальной настройки отредактируйте `backend/config/settings.py`.

## 🌐 Локализация

Поддерживаемые языки:
- 🇷🇺 Русский (ru)
- 🇺🇸 Английский (en)
- 🇹🇭 Тайский (th)
- 🇨🇳 Китайский (zh)

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

## 🚀 Развертывание

### Продакшн
1. Создайте `.env.production` с продакшн настройками
2. Настройте веб-сервер (Nginx + Gunicorn)
3. Настройте базу данных PostgreSQL

### Docker
```bash
docker build -t realestate-platform .
docker run -p 8002:8002 realestate-platform
```

## 📊 Аналитика

Поддерживаемые системы аналитики:
- Google Analytics
- Yandex Metrika
- Facebook Pixel

Настройте в `.env` файле:
```env
GOOGLE_ANALYTICS_ID=GA_MEASUREMENT_ID
YANDEX_METRIKA_ID=YOUR_METRIKA_ID
FACEBOOK_PIXEL_ID=YOUR_PIXEL_ID
```

## 🛡️ Безопасность

- Все пароли хешируются
- CSRF защита
- SQL инъекции предотвращены
- XSS защита
- HTTPS поддержка

## 📚 Документация

- [WHITE_LABEL_GUIDE.md](WHITE_LABEL_GUIDE.md) - Подробное руководство по кастомизации
- [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) - Краткое руководство
- [config.env.example](config.env.example) - Пример конфигурации

## 🤝 Поддержка

- Создайте issue в репозитории
- Обратитесь к документации
- Проверьте примеры в папке `examples/`

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для подробностей.

## 🎯 Roadmap

- [ ] Интеграция с CRM системами
- [ ] Мобильное приложение
- [ ] Виртуальные туры
- [ ] Система отзывов
- [ ] Интеграция с платежными системами
- [ ] API для внешних интеграций

---

**Создайте свой уникальный сайт недвижимости! 🏠✨** 