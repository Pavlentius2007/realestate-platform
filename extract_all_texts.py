#!/usr/bin/env python
"""
Скрипт для извлечения всех русских текстов из HTML шаблонов
и автоматического добавления их в файлы переводов
"""

import os
import re
from pathlib import Path
from typing import Set, Dict, List, Optional
import polib

def extract_russian_texts_from_html(file_path: Path) -> Set[str]:
    """Извлекает русские тексты из HTML файла"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Ошибка чтения файла {file_path}: {e}")
        return set()
    
    # Паттерны для поиска русского текста
    patterns = [
        # Русский текст в кавычках
        r'"([^"]*[А-Я][а-я][^"]*)"',
        r"'([^']*[А-Я][а-я][^']*)'",
        
        # Русский текст между тегами (без HTML тегов)
        r'>([^<]*[А-Я][а-я][^<]*)<',
        
        # Placeholder и value атрибуты
        r'placeholder="([^"]*[А-Я][а-я][^"]*)"',
        r'value="([^"]*[А-Я][а-я][^"]*)"',
        r'title="([^"]*[А-Я][а-я][^"]*)"',
        r'alt="([^"]*[А-Я][а-я][^"]*)"',
        
        # JavaScript строки
        r'alert\([\'"]([^"\']*[А-Я][а-я][^"\']*)[\'"]',
        r'innerText\s*=\s*[\'"]([^"\']*[А-Я][а-я][^"\']*)[\'"]',
        r'textContent\s*=\s*[\'"]([^"\']*[А-Я][а-я][^"\']*)[\'"]',
    ]
    
    texts = set()
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        for match in matches:
            # Очищаем текст от лишних символов
            text = match.strip()
            
            # Пропускаем слишком короткие или технические строки
            if len(text) < 2:
                continue
            
            # Пропускаем URLs, CSS классы, и т.д.
            if any(skip in text.lower() for skip in ['http', 'www', 'class=', 'id=', '.css', '.js', 'px;', '%']):
                continue
                
            # Пропускаем эмодзи без текста
            if re.match(r'^[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\s]*$', text):
                continue
            
            # Добавляем текст с русскими буквами
            if re.search(r'[А-Я][а-я]', text):
                texts.add(text)
    
    return texts

def scan_all_templates(templates_dir: Path) -> Dict[str, Set[str]]:
    """Сканирует все HTML шаблоны и извлекает русские тексты"""
    
    all_texts = {}
    
    # Ищем все HTML файлы
    for html_file in templates_dir.glob('**/*.html'):
        print(f"🔍 Сканирую: {html_file.relative_to(templates_dir)}")
        
        texts = extract_russian_texts_from_html(html_file)
        if texts:
            all_texts[str(html_file.relative_to(templates_dir))] = texts
            print(f"   Найдено {len(texts)} текстов")
        else:
            print(f"   Русских текстов не найдено")
    
    return all_texts

def add_to_po_file(po_file_path: Path, texts: Set[str]):
    """Добавляет тексты в .po файл"""
    
    try:
        # Загружаем существующий файл или создаем новый
        if po_file_path.exists():
            po = polib.pofile(str(po_file_path))
        else:
            po = polib.POFile()
            po.metadata = {
                'Project-Id-Version': 'Sianoro Real Estate',
                'Report-Msgid-Bugs-To': 'admin@sianoro.com',
                'Language': po_file_path.parent.parent.name,
                'MIME-Version': '1.0',
                'Content-Type': 'text/plain; charset=utf-8',
                'Content-Transfer-Encoding': '8bit',
            }
        
        # Получаем существующие msgid
        existing_msgids = {entry.msgid for entry in po}
        
        added_count = 0
        for text in texts:
            if text not in existing_msgids:
                entry = polib.POEntry(
                    msgid=text,
                    msgstr='',  # Пустой перевод - нужно будет заполнить
                    comment=f'Автоматически извлечено из HTML шаблонов'
                )
                po.append(entry)
                added_count += 1
        
        # Сохраняем файл
        po.save(str(po_file_path))
        print(f"   ✅ Добавлено {added_count} новых записей в {po_file_path.name}")
        
        return added_count
        
    except Exception as e:
        print(f"   ❌ Ошибка при работе с {po_file_path}: {e}")
        return 0

def create_translations_for_language(lang: str, all_texts: Set[str], base_translations: Optional[Dict[str, str]] = None):
    """Создает переводы для указанного языка"""
    
    translations_dir = Path("backend/translations")
    po_file_path = translations_dir / lang / "LC_MESSAGES" / "messages.po"
    
    # Создаем директории если их нет
    po_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Загружаем или создаем .po файл
    if po_file_path.exists():
        po = polib.pofile(str(po_file_path))
    else:
        po = polib.POFile()
        po.metadata = {
            'Project-Id-Version': 'Sianoro Real Estate',
            'Report-Msgid-Bugs-To': 'admin@sianoro.com',
            'Language': lang,
            'MIME-Version': '1.0',
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Transfer-Encoding': '8bit',
        }
    
    # Добавляем тексты
    existing_msgids = {entry.msgid for entry in po}
    added_count = 0
    
    for text in all_texts:
        if text not in existing_msgids:
            # Пытаемся найти перевод в базовых переводах
            translation = ''
            if base_translations and text in base_translations:
                translation = base_translations[text]
            
            entry = polib.POEntry(
                msgid=text,
                msgstr=translation,
                comment='Автоматически извлечено из HTML шаблонов'
            )
            po.append(entry)
            added_count += 1
    
    # Сохраняем
    po.save(str(po_file_path))
    print(f"✅ {lang}: добавлено {added_count} записей")
    
    return added_count

def main():
    """Основная функция"""
    
    print("🚀 Извлечение русских текстов из HTML шаблонов")
    print("=" * 50)
    
    # Определяем пути
    templates_dir = Path("backend/templates")
    translations_dir = Path("backend/translations")
    
    if not templates_dir.exists():
        print(f"❌ Директория шаблонов не найдена: {templates_dir}")
        return
    
    # Сканируем все шаблоны
    print("\n🔍 Сканирование шаблонов...")
    all_texts_by_file = scan_all_templates(templates_dir)
    
    # Объединяем все тексты
    all_texts = set()
    for file_texts in all_texts_by_file.values():
        all_texts.update(file_texts)
    
    print(f"\n📊 Всего найдено уникальных русских текстов: {len(all_texts)}")
    
    if not all_texts:
        print("❌ Русские тексты не найдены")
        return
    
    # Показываем примеры найденных текстов
    print("\n📝 Примеры найденных текстов:")
    for i, text in enumerate(sorted(list(all_texts))[:10]):
        print(f"   {i+1}. {text}")
    
    if len(all_texts) > 10:
        print(f"   ... и еще {len(all_texts) - 10} текстов")
    
    # Базовые переводы для английского (можно расширить)
    base_en_translations = {
        "Недвижимость в Паттайе": "Real Estate in Pattaya",
        "Найдите идеальную недвижимость с помощью умного поиска": "Find perfect property with smart search",
        "Поиск недвижимости": "Property Search",
        "Купить": "Buy",
        "Снять": "Rent",
        "Аренда": "Rent",
        "Новостройки": "New Projects",
        "Проекты": "Projects",
        "Избранное": "Favorites",
        "О нас": "About Us",
        "Контакты": "Contacts",
        "Админка": "Admin",
        "Регистрация": "Registration",
        "Полезное": "Useful",
        "Статьи": "Articles",
        "Главная": "Home",
    }
    
    # Создаем переводы для всех языков
    print(f"\n🌍 Создание переводов...")
    languages = ['en', 'th', 'zh']
    
    for lang in languages:
        if lang == 'en':
            create_translations_for_language(lang, all_texts, base_en_translations)
        else:
            create_translations_for_language(lang, all_texts)
    
    print(f"\n🎯 Готово! Теперь нужно:")
    print(f"   1. Заполнить переводы в .po файлах")
    print(f"   2. Скомпилировать переводы: python backend/compile_translations.py")
    print(f"   3. Добавить функции _() в шаблоны где нужно")

if __name__ == "__main__":
    # Проверяем наличие polib
    try:
        import polib
    except ImportError:
        print("❌ Модуль polib не установлен")
        print("💡 Установите: pip install polib")
        exit(1)
    
    main() 