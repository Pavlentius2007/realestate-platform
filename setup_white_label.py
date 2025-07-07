#!/usr/bin/env python3
"""
Скрипт для быстрой настройки white label решения
Помогает настроить брендинг, контакты и другие параметры
"""

import os
import shutil
from pathlib import Path
import json

def print_banner():
    """Выводит баннер"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                    🎨 WHITE LABEL SETUP                      ║
║                                                              ║
║  Быстрая настройка платформы недвижимости под ваш бренд     ║
╚══════════════════════════════════════════════════════════════╝
    """)

def get_input(prompt, default=""):
    """Получает ввод от пользователя"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()

def create_env_file():
    """Создает .env файл с настройками"""
    print("\n🔧 Настройка конфигурации...")
    
    # Брендинг
    print("\n📋 БРЕНДИНГ:")
    brand_name = get_input("Название компании", "Sianoro")
    brand_tagline = get_input("Слоган компании", "Ваш надежный партнер в сфере недвижимости в Таиланде")
    primary_color = get_input("Основной цвет (hex)", "#0074E4")
    secondary_color = get_input("Вторичный цвет (hex)", "#005bb5")
    
    # Контакты
    print("\n📞 КОНТАКТЫ:")
    contact_phone = get_input("Телефон", "+66 95 386 2858")
    contact_whatsapp = get_input("WhatsApp", "+66 95 386 2858")
    contact_telegram = get_input("Telegram", "t.me/InvestThailand")
    contact_email = get_input("Email", "info@sianoro.com")
    contact_address = get_input("Адрес офиса", "Паттайя, Таиланд")
    
    # SEO
    print("\n🔍 SEO:")
    site_title = get_input("Заголовок сайта", f"{brand_name} - Недвижимость в Таиланде")
    site_description = get_input("Описание сайта", "Найдите идеальную недвижимость для жизни и инвестиций в Паттайе")
    site_keywords = get_input("Ключевые слова", "недвижимость, таиланд, паттайя, квартиры, виллы, инвестиции")
    
    # Функции
    print("\n⚙️ ФУНКЦИИ:")
    enable_calculator = get_input("Включить калькулятор? (y/n)", "y").lower() == "y"
    enable_ai_assistant = get_input("Включить ИИ-ассистент? (y/n)", "y").lower() == "y"
    enable_favorites = get_input("Включить избранное? (y/n)", "y").lower() == "y"
    enable_articles = get_input("Включить статьи? (y/n)", "y").lower() == "y"
    
    # Аналитика
    print("\n📊 АНАЛИТИКА:")
    google_analytics = get_input("Google Analytics ID (оставьте пустым если не нужно)", "")
    yandex_metrika = get_input("Yandex Metrika ID (оставьте пустым если не нужно)", "")
    facebook_pixel = get_input("Facebook Pixel ID (оставьте пустым если не нужно)", "")
    
    # Создаем содержимое .env файла
    env_content = f"""# ========================================
# WHITE LABEL CONFIGURATION
# ========================================
# Автоматически сгенерировано скриптом setup_white_label.py

# ========================================
# БРЕНДИНГ
# ========================================
BRAND_NAME={brand_name}
BRAND_TAGLINE={brand_tagline}
PRIMARY_COLOR={primary_color}
SECONDARY_COLOR={secondary_color}
ACCENT_COLOR=#3b82f6

# ========================================
# КОНТАКТЫ
# ========================================
CONTACT_PHONE={contact_phone}
CONTACT_WHATSAPP={contact_whatsapp}
CONTACT_TELEGRAM={contact_telegram}
CONTACT_EMAIL={contact_email}
CONTACT_ADDRESS={contact_address}

# ========================================
# ФУНКЦИИ
# ========================================
ENABLE_CALCULATOR={'true' if enable_calculator else 'false'}
ENABLE_AI_ASSISTANT={'true' if enable_ai_assistant else 'false'}
ENABLE_FAVORITES={'true' if enable_favorites else 'false'}
ENABLE_ARTICLES={'true' if enable_articles else 'false'}
ENABLE_PROJECTS=true
ENABLE_RENTAL=true

# ========================================
# АНАЛИТИКА
# ========================================
GOOGLE_ANALYTICS_ID={google_analytics}
YANDEX_METRIKA_ID={yandex_metrika}
FACEBOOK_PIXEL_ID={facebook_pixel}

# ========================================
# SEO
# ========================================
SITE_TITLE={site_title}
SITE_DESCRIPTION={site_description}
SITE_KEYWORDS={site_keywords}

# ========================================
# ПЛАТЕЖИ
# ========================================
CURRENCY=THB
CURRENCY_SYMBOL=฿
ENABLE_PAYMENTS=false

# ========================================
# БАЗА ДАННЫХ
# ========================================
DATABASE_URL=sqlite:///./realestate.db

# ========================================
# БЕЗОПАСНОСТЬ
# ========================================
SECRET_KEY=your-super-secret-key-here-change-this-in-production
"""
    
    # Записываем .env файл
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print("✅ Файл .env создан успешно!")

def update_config_files():
    """Обновляет конфигурационные файлы"""
    print("\n🔧 Обновление конфигурационных файлов...")
    
    # Загружаем .env файл
    env_vars = {}
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key] = value
    
    # Обновляем настройки в коде
    update_settings_file(env_vars)
    
    print("✅ Конфигурационные файлы обновлены!")

def update_settings_file(env_vars):
    """Обновляет файл настроек"""
    settings_file = "backend/config/settings.py"
    
    if not os.path.exists(settings_file):
        print(f"⚠️ Файл {settings_file} не найден, пропускаем...")
        return
    
    # Читаем текущий файл
    with open(settings_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Обновляем значения по умолчанию
    if "BRAND_NAME" in env_vars:
        content = content.replace('name: str = "Sianoro"', f'name: str = "{env_vars["BRAND_NAME"]}"')
    
    if "BRAND_TAGLINE" in env_vars:
        content = content.replace('tagline: str = "Ваш надежный партнер в сфере недвижимости в Таиланде"', 
                                f'tagline: str = "{env_vars["BRAND_TAGLINE"]}"')
    
    if "PRIMARY_COLOR" in env_vars:
        content = content.replace('primary_color: str = "#0074E4"', f'primary_color: str = "{env_vars["PRIMARY_COLOR"]}"')
    
    if "CONTACT_PHONE" in env_vars:
        content = content.replace('phone: str = "+66 95 386 2858"', f'phone: str = "{env_vars["CONTACT_PHONE"]}"')
    
    if "CONTACT_WHATSAPP" in env_vars:
        content = content.replace('whatsapp: str = "+66 95 386 2858"', f'whatsapp: str = "{env_vars["CONTACT_WHATSAPP"]}"')
    
    if "CONTACT_TELEGRAM" in env_vars:
        content = content.replace('telegram: str = "t.me/InvestThailand"', f'telegram: str = "{env_vars["CONTACT_TELEGRAM"]}"')
    
    if "CONTACT_EMAIL" in env_vars:
        content = content.replace('email: str = "info@sianoro.com"', f'email: str = "{env_vars["CONTACT_EMAIL"]}"')
    
    # Записываем обновленный файл
    with open(settings_file, "w", encoding="utf-8") as f:
        f.write(content)

def create_brand_assets():
    """Создает структуру для брендинга"""
    print("\n🎨 Создание структуры для брендинга...")
    
    # Создаем папки если их нет
    brand_dirs = [
        "static/img/brand",
        "static/css/themes",
        "static/js/custom"
    ]
    
    for dir_path in brand_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Создаем README для брендинга
    brand_readme = """# 🎨 Брендинг

Замените файлы в этой папке на ваши:

## Обязательные файлы:
- `logo.png` - ваш логотип (рекомендуемый размер: 200x60px)
- `favicon.ico` - иконка сайта (16x16px, 32x32px)
- `og-image.jpg` - изображение для соцсетей (1200x630px)

## Дополнительные файлы:
- `hero-bg.jpg` - фоновое изображение для главной страницы
- `about-image.jpg` - изображение для страницы "О нас"

## Стили:
Создайте файл `static/css/themes/custom.css` для ваших стилей.
"""
    
    with open("static/img/brand/README.md", "w", encoding="utf-8") as f:
        f.write(brand_readme)
    
    print("✅ Структура для брендинга создана!")

def create_customization_guide():
    """Создает руководство по кастомизации"""
    print("\n📖 Создание руководства по кастомизации...")
    
    guide_content = f"""# 🎨 Руководство по кастомизации

## Быстрый старт

1. Замените файлы в `static/img/brand/` на ваши
2. Отредактируйте `.env` файл под ваши нужды
3. Запустите сервер: `python run_server.py`

## Основные файлы для кастомизации:

### Брендинг:
- `static/img/brand/logo.png` - ваш логотип
- `static/img/brand/favicon.ico` - иконка сайта
- `static/img/brand/og-image.jpg` - изображение для соцсетей

### Стили:
- `static/css/themes/custom.css` - ваши кастомные стили
- `backend/config/themes.py` - создание новых тем

### Конфигурация:
- `.env` - основные настройки
- `backend/config/settings.py` - продвинутые настройки

## Поддержка:
- Документация: `WHITE_LABEL_GUIDE.md`
- Примеры: папка `examples/`
"""
    
    with open("CUSTOMIZATION_GUIDE.md", "w", encoding="utf-8") as f:
        f.write(guide_content)
    
    print("✅ Руководство по кастомизации создано!")

def main():
    """Основная функция"""
    print_banner()
    
    print("Этот скрипт поможет настроить платформу под ваш бренд.")
    print("Следуйте инструкциям и введите необходимую информацию.\n")
    
    # Проверяем, существует ли уже .env файл
    if os.path.exists(".env"):
        overwrite = input("Файл .env уже существует. Перезаписать? (y/n): ").lower()
        if overwrite != "y":
            print("Настройка отменена.")
            return
    
    try:
        # Создаем .env файл
        create_env_file()
        
        # Обновляем конфигурационные файлы
        update_config_files()
        
        # Создаем структуру для брендинга
        create_brand_assets()
        
        # Создаем руководство
        create_customization_guide()
        
        print("\n" + "="*60)
        print("🎉 НАСТРОЙКА ЗАВЕРШЕНА!")
        print("="*60)
        print("\nСледующие шаги:")
        print("1. Замените файлы в static/img/brand/ на ваши")
        print("2. Отредактируйте .env файл если нужно")
        print("3. Запустите сервер: python run_server.py")
        print("4. Откройте http://localhost:8002/ru")
        print("\nДокументация:")
        print("- WHITE_LABEL_GUIDE.md - подробное руководство")
        print("- CUSTOMIZATION_GUIDE.md - краткое руководство")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("Попробуйте запустить скрипт снова или настройте вручную.")

if __name__ == "__main__":
    main() 