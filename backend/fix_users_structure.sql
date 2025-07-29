-- Исправление структуры таблицы users
-- Проблема: поле name имеет ограничение NOT NULL, но код использует full_name

-- 1. Убираем ограничение NOT NULL с поля name
ALTER TABLE users ALTER COLUMN name DROP NOT NULL;

-- 2. Проверяем что full_name есть в таблице (на всякий случай)
-- Если не существует - добавляем
DO $$
BEGIN
    IF NOT EXISTS (SELECT column_name FROM information_schema.columns 
                   WHERE table_name='users' AND column_name='full_name') THEN
        ALTER TABLE users ADD COLUMN full_name VARCHAR;
    END IF;
END $$;

-- 3. Заполняем full_name данными из name (где возможно)
UPDATE users SET full_name = name WHERE name IS NOT NULL AND (full_name IS NULL OR full_name = '');

-- 4. Проверяем что все нужные поля есть
DO $$
BEGIN
    -- Добавляем whatsapp_number если не существует
    IF NOT EXISTS (SELECT column_name FROM information_schema.columns 
                   WHERE table_name='users' AND column_name='whatsapp_number') THEN
        ALTER TABLE users ADD COLUMN whatsapp_number VARCHAR;
    END IF;
    
    -- Добавляем telegram_id если не существует
    IF NOT EXISTS (SELECT column_name FROM information_schema.columns 
                   WHERE table_name='users' AND column_name='telegram_id') THEN
        ALTER TABLE users ADD COLUMN telegram_id VARCHAR;
    END IF;
    
    -- Добавляем instagram_id если не существует
    IF NOT EXISTS (SELECT column_name FROM information_schema.columns 
                   WHERE table_name='users' AND column_name='instagram_id') THEN
        ALTER TABLE users ADD COLUMN instagram_id VARCHAR;
    END IF;
    
    -- Добавляем hashed_password если не существует
    IF NOT EXISTS (SELECT column_name FROM information_schema.columns 
                   WHERE table_name='users' AND column_name='hashed_password') THEN
        ALTER TABLE users ADD COLUMN hashed_password VARCHAR;
    END IF;
END $$;

-- 5. Показываем результат
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY column_name; 