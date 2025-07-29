
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
