#!/usr/bin/env python
"""
Система автоматического перевода для новых статей и объектов недвижимости
"""

import os
import asyncio
from typing import Dict, List, Optional
from pathlib import Path
import polib
import json

# Для работы с Google Translate
try:
    from googletrans import Translator
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False
    print("⚠️ googletrans не установлен. Установите: pip install googletrans==3.1.0a0")

class AutoTranslator:
    """Автоматический переводчик для контента сайта"""
    
    def __init__(self):
        self.translator = Translator() if GOOGLETRANS_AVAILABLE else None
        self.supported_languages = {
            'en': 'English',
            'th': 'Thai', 
            'zh': 'Chinese',
            'ru': 'Russian'
        }
        self.translations_dir = Path("backend/translations")
        
    def translate_text(self, text: str, target_lang: str, source_lang: str = 'ru') -> str:
        """Переводит текст с помощью Google Translate"""
        
        if not self.translator:
            print("❌ Google Translator недоступен")
            return text
            
        try:
            # Убираем лишние пробелы и переносы
            clean_text = ' '.join(text.split())
            
            if len(clean_text.strip()) == 0:
                return text
                
            # Переводим
            result = self.translator.translate(
                clean_text, 
                src=source_lang, 
                dest=target_lang
            )
            
            translated = result.text if result else text
            print(f"✅ Переведено ({source_lang}→{target_lang}): {clean_text[:50]}... → {translated[:50]}...")
            
            return translated
            
        except Exception as e:
            print(f"❌ Ошибка перевода: {e}")
            return text

def create_translation_hooks_sql():
    """Создает SQL-скрипт для автоматических триггеров перевода"""
    
    sql_content = """
-- SQL скрипт для автоматического запуска переводов
-- Выполните этот скрипт в PGAdmin4 для настройки автоматических переводов

-- 1. Добавляем колонки для переводов в таблицу properties (если их нет)
DO $$ 
BEGIN
    -- Добавляем колонки для английского языка
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='properties' AND column_name='title_en') THEN
        ALTER TABLE properties ADD COLUMN title_en TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='properties' AND column_name='description_en') THEN
        ALTER TABLE properties ADD COLUMN description_en TEXT;
    END IF;
    
    -- Добавляем колонки для тайского языка
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='properties' AND column_name='title_th') THEN
        ALTER TABLE properties ADD COLUMN title_th TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='properties' AND column_name='description_th') THEN
        ALTER TABLE properties ADD COLUMN description_th TEXT;
    END IF;
    
    -- Добавляем колонки для китайского языка
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='properties' AND column_name='title_zh') THEN
        ALTER TABLE properties ADD COLUMN title_zh TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='properties' AND column_name='description_zh') THEN
        ALTER TABLE properties ADD COLUMN description_zh TEXT;
    END IF;
END $$;

-- 2. Создаем таблицу для очереди переводов
CREATE TABLE IF NOT EXISTS translation_queue (
    id SERIAL PRIMARY KEY,
    content_type VARCHAR(50) NOT NULL, -- 'property' или 'article'
    content_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    error_message TEXT
);

-- 3. Создаем функцию для добавления в очередь переводов
CREATE OR REPLACE FUNCTION add_to_translation_queue()
RETURNS TRIGGER AS $$
BEGIN
    -- Добавляем новый объект в очередь переводов
    INSERT INTO translation_queue (content_type, content_id)
    VALUES (TG_ARGV[0], NEW.id);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 4. Создаем триггеры для автоматического добавления в очередь
-- Триггер для новых объектов недвижимости
DROP TRIGGER IF EXISTS auto_translate_property ON properties;
CREATE TRIGGER auto_translate_property
    AFTER INSERT ON properties
    FOR EACH ROW
    EXECUTE FUNCTION add_to_translation_queue('property');

COMMENT ON TABLE translation_queue IS 'Очередь для автоматического перевода нового контента';
"""
    
    with open('setup_translation_hooks.sql', 'w', encoding='utf-8') as f:
        f.write(sql_content)
    
    print("✅ Создан файл setup_translation_hooks.sql")
    print("💡 Выполните этот скрипт в PGAdmin4 для настройки автоматических переводов")

if __name__ == "__main__":
    print("🤖 Система автоматического перевода")
    print("=" * 50)
    
    # Создаем SQL-скрипт для настройки
    create_translation_hooks_sql()
    
    # Пример использования
    if GOOGLETRANS_AVAILABLE:
        translator = AutoTranslator()
        
        # Тестируем перевод
        test_text = "Красивая квартира с видом на море в центре Паттайи"
        
        print(f"\n🧪 Тест перевода:")
        print(f"Оригинал: {test_text}")
        
        for lang in ['en', 'th', 'zh']:
            translated = translator.translate_text(test_text, lang)
            print(f"{lang}: {translated}")
    
    print(f"\n💡 Следующие шаги:")
    print(f"   1. Установите: pip install googletrans==3.1.0a0")
    print(f"   2. Выполните setup_translation_hooks.sql в PGAdmin4")
    print(f"   3. Создайте фоновую задачу для обработки переводов") 