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
from deep_translator import GoogleTranslator

# Для работы с базой данных
try:
    import asyncpg
    import asyncio
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    print("⚠️ asyncpg не установлен. Установите: pip install asyncpg")

class AutoTranslator:
    """Автоматический переводчик для контента сайта"""
    
    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'th': 'Thai', 
            'zh': 'Chinese',
            'ru': 'Russian'
        }
        self.translations_dir = Path("backend/translations")
        
    def translate_text(self, text: str, target_lang: str, source_lang: str = 'ru') -> str:
        """Переводит текст с помощью deep-translator"""
        try:
            clean_text = ' '.join(text.split())
            if len(clean_text.strip()) == 0:
                return text
            translated = GoogleTranslator(source=source_lang, target=target_lang).translate(clean_text)
            print(f"✅ Переведено ({source_lang}→{target_lang}): {clean_text[:50]}... → {translated[:50]}...")
            return translated
        except Exception as e:
            print(f"❌ Ошибка перевода: {e}")
            return text
    
    def translate_property_fields(self, property_data: Dict, target_langs: Optional[List[str]] = None) -> Dict:
        """Переводит поля объекта недвижимости"""
        
        if target_langs is None:
            target_langs = ['en', 'th', 'zh']
        
        translated_data = property_data.copy()
        
        # Поля для перевода
        fields_to_translate = [
            'title', 'description', 'location', 'amenities', 
            'nearby_attractions', 'transportation'
        ]
        
        for field in fields_to_translate:
            if field in property_data and property_data[field]:
                original_text = property_data[field]
                
                # Создаем переводы для каждого языка
                for lang in target_langs:
                    translated_text = self.translate_text(original_text, lang)
                    translated_data[f"{field}_{lang}"] = translated_text
        
        return translated_data
    
    def translate_article_content(self, article_data: Dict, target_langs: Optional[List[str]] = None) -> Dict:
        """Переводит содержимое статьи"""
        
        if target_langs is None:
            target_langs = ['en', 'th', 'zh']
        
        translated_data = article_data.copy()
        
        # Поля статьи для перевода
        fields_to_translate = [
            'title', 'excerpt', 'content', 'meta_description'
        ]
        
        for field in fields_to_translate:
            if field in article_data and article_data[field]:
                original_text = article_data[field]
                
                # Переводим по частям если текст большой
                if len(original_text) > 4000:
                    # Разбиваем на абзацы
                    paragraphs = original_text.split('\n\n')
                    translated_paragraphs = {}
                    
                    for lang in target_langs:
                        translated_parts = []
                        for paragraph in paragraphs:
                            if paragraph.strip():
                                translated_part = self.translate_text(paragraph.strip(), lang)
                                translated_parts.append(translated_part)
                            else:
                                translated_parts.append('')
                        
                        translated_paragraphs[lang] = '\n\n'.join(translated_parts)
                    
                    for lang in target_langs:
                        translated_data[f"{field}_{lang}"] = translated_paragraphs[lang]
                else:
                    # Короткий текст переводим целиком
                    for lang in target_langs:
                        translated_text = self.translate_text(original_text, lang)
                        translated_data[f"{field}_{lang}"] = translated_text
        
        return translated_data
    
    def add_translations_to_po_files(self, translations: Dict[str, str]):
        """Добавляет переводы в .po файлы"""
        
        for lang in self.supported_languages:
            if lang == 'ru':  # Пропускаем русский - он источник
                continue
                
            po_file_path = self.translations_dir / lang / "LC_MESSAGES" / "messages.po"
            
            if not po_file_path.exists():
                print(f"⚠️ Файл {po_file_path} не найден")
                continue
            
            try:
                po = polib.pofile(str(po_file_path))
                
                # Получаем существующие записи
                existing_msgids = {entry.msgid for entry in po}
                
                added_count = 0
                updated_count = 0
                
                for russian_text, translation in translations.items():
                    if russian_text in existing_msgids:
                        # Обновляем существующий перевод если он пустой
                        for entry in po:
                            if entry.msgid == russian_text and not entry.msgstr:
                                entry.msgstr = translation
                                updated_count += 1
                                break
                    else:
                        # Добавляем новый перевод
                        entry = polib.POEntry(
                            msgid=russian_text,
                            msgstr=translation,
                            comment='Автоматически переведено'
                        )
                        po.append(entry)
                        added_count += 1
                
                po.save(str(po_file_path))
                
                if added_count > 0 or updated_count > 0:
                    print(f"✅ {lang}: добавлено {added_count}, обновлено {updated_count} переводов")
                    
            except Exception as e:
                print(f"❌ Ошибка при работе с {lang}: {e}")
    
    async def translate_new_property(self, property_id: int, db_config: Dict):
        """Переводит новый объект недвижимости в базе данных"""
        
        if not ASYNCPG_AVAILABLE:
            print("❌ asyncpg недоступен для работы с БД")
            return
        
        try:
            conn = await asyncpg.connect(**db_config)
            
            # Получаем данные объекта
            property_data = await conn.fetchrow(
                "SELECT * FROM properties WHERE id = $1", property_id
            )
            
            if not property_data:
                print(f"❌ Объект с ID {property_id} не найден")
                return
            
            # Переводим поля
            translated_data = self.translate_property_fields(dict(property_data))
            
            # Обновляем в базе данных
            update_fields = []
            update_values = []
            
            for field, value in translated_data.items():
                if field.endswith(('_en', '_th', '_zh')):
                    update_fields.append(f"{field} = ${len(update_values) + 1}")
                    update_values.append(value)
            
            if update_fields:
                update_values.append(property_id)
                update_query = f"""
                    UPDATE properties 
                    SET {', '.join(update_fields)}
                    WHERE id = ${len(update_values)}
                """
                
                await conn.execute(update_query, *update_values)
                print(f"✅ Объект {property_id} переведен на {len(['en', 'th', 'zh'])} языков")
            
            await conn.close()
            
        except Exception as e:
            print(f"❌ Ошибка при переводе объекта {property_id}: {e}")
    
    async def translate_new_article(self, article_id: int, db_config: Dict):
        """Переводит новую статью в базе данных"""
        
        if not ASYNCPG_AVAILABLE:
            print("❌ asyncpg недоступен для работы с БД")
            return
        
        try:
            conn = await asyncpg.connect(**db_config)
            
            # Получаем данные статьи
            article_data = await conn.fetchrow(
                "SELECT * FROM articles WHERE id = $1", article_id
            )
            
            if not article_data:
                print(f"❌ Статья с ID {article_id} не найдена")
                return
            
            # Переводим содержимое
            translated_data = self.translate_article_content(dict(article_data))
            
            # Обновляем в базе данных
            update_fields = []
            update_values = []
            
            for field, value in translated_data.items():
                if field.endswith(('_en', '_th', '_zh')):
                    update_fields.append(f"{field} = ${len(update_values) + 1}")
                    update_values.append(value)
            
            if update_fields:
                update_values.append(article_id)
                update_query = f"""
                    UPDATE articles 
                    SET {', '.join(update_fields)}
                    WHERE id = ${len(update_values)}
                """
                
                await conn.execute(update_query, *update_values)
                print(f"✅ Статья {article_id} переведена на {len(['en', 'th', 'zh'])} языков")
            
            await conn.close()
            
        except Exception as e:
            print(f"❌ Ошибка при переводе статьи {article_id}: {e}")

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

-- Триггер для новых статей (если таблица articles существует)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'articles') THEN
        EXECUTE 'DROP TRIGGER IF EXISTS auto_translate_article ON articles';
        EXECUTE 'CREATE TRIGGER auto_translate_article
                    AFTER INSERT ON articles
                    FOR EACH ROW
                    EXECUTE FUNCTION add_to_translation_queue(''article'')';
    END IF;
END $$;

-- 5. Создаем индексы для производительности
CREATE INDEX IF NOT EXISTS idx_translation_queue_status ON translation_queue(status);
CREATE INDEX IF NOT EXISTS idx_translation_queue_created ON translation_queue(created_at);

COMMENT ON TABLE translation_queue IS 'Очередь для автоматического перевода нового контента';
"""
    
    with open('setup_translation_hooks.sql', 'w', encoding='utf-8') as f:
        f.write(sql_content)
    
    print("✅ Создан файл setup_translation_hooks.sql")
    print("💡 Выполните этот скрипт в PGAdmin4 для настройки автоматических переводов")

async def process_translation_queue(db_config: Dict):
    """Обрабатывает очередь переводов"""
    
    if not ASYNCPG_AVAILABLE:
        print("❌ asyncpg недоступен")
        return
    
    translator = AutoTranslator()
    
    try:
        conn = await asyncpg.connect(**db_config)
        
        # Получаем pending переводы
        pending_translations = await conn.fetch("""
            SELECT id, content_type, content_id 
            FROM translation_queue 
            WHERE status = 'pending'
            ORDER BY created_at ASC
            LIMIT 10
        """)
        
        for row in pending_translations:
            queue_id, content_type, content_id = row
            
            try:
                # Отмечаем как обрабатываемый
                await conn.execute(
                    "UPDATE translation_queue SET status = 'processing', processed_at = NOW() WHERE id = $1",
                    queue_id
                )
                
                # Переводим контент
                if content_type == 'property':
                    await translator.translate_new_property(content_id, db_config)
                elif content_type == 'article':
                    await translator.translate_new_article(content_id, db_config)
                
                # Отмечаем как завершенный
                await conn.execute(
                    "UPDATE translation_queue SET status = 'completed' WHERE id = $1",
                    queue_id
                )
                
                print(f"✅ Обработан {content_type} ID {content_id}")
                
            except Exception as e:
                # Отмечаем как ошибочный
                await conn.execute(
                    "UPDATE translation_queue SET status = 'failed', error_message = $1 WHERE id = $2",
                    str(e), queue_id
                )
                print(f"❌ Ошибка обработки {content_type} ID {content_id}: {e}")
        
        await conn.close()
        
        if pending_translations:
            print(f"✅ Обработано {len(pending_translations)} элементов из очереди")
        else:
            print("📭 Очередь переводов пуста")
            
    except Exception as e:
        print(f"❌ Ошибка при обработке очереди: {e}")

if __name__ == "__main__":
    print("🤖 Система автоматического перевода")
    print("=" * 50)
    
    # Создаем SQL-скрипт для настройки
    create_translation_hooks_sql()
    
    # Пример использования
    translator = AutoTranslator()
    
    # Тестируем перевод
    test_text = "Красивая квартира с видом на море в центре Паттайи"
    
    print(f"\n🧪 Тест перевода:")
    print(f"Оригинал: {test_text}")
    
    for lang in ['en', 'th', 'zh']:
        translated = translator.translate_text(test_text, lang)
        print(f"{lang}: {translated}")
    
    print(f"\n💡 Следующие шаги:")
    print(f"   1. Установите: pip install asyncpg")
    print(f"   2. Выполните setup_translation_hooks.sql в PGAdmin4")
    print(f"   3. Запустите обработчик очереди: python auto_translate.py") 