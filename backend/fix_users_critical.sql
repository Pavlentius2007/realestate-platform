-- ============================================================================
-- 🚨 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ ТАБЛИЦЫ USERS
-- Решает ошибки из логов приложения
-- Выполните этот скрипт в PGAdmin4
-- ============================================================================

-- ПРОБЛЕМА 1: значение NULL в столбце "name" нарушает ограничение NOT NULL
-- РЕШЕНИЕ: Убираем ограничение NOT NULL с поля name
-- ----------------------------------------------------------------------------

ALTER TABLE users ALTER COLUMN name DROP NOT NULL;
SELECT '✅ Ограничение NOT NULL убрано с поля name' as status;

-- ПРОБЛЕМА 2: столбец users.hashed_password не существует  
-- РЕШЕНИЕ: Добавляем недостающее поле hashed_password
-- ----------------------------------------------------------------------------

ALTER TABLE users ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255);
SELECT '✅ Поле hashed_password добавлено' as status;

-- ДОПОЛНИТЕЛЬНЫЕ ИСПРАВЛЕНИЯ: Убеждаемся что все нужные поля есть
-- ----------------------------------------------------------------------------

-- Добавляем недостающие поля если их нет
ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(255);  
ALTER TABLE users ADD COLUMN IF NOT EXISTS telegram_id VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS whatsapp_number VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS instagram_id VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS source VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

SELECT '✅ Все недостающие поля добавлены' as status;

-- ПЕРЕНОС ДАННЫХ: Копируем данные из name в full_name (где возможно)
-- ----------------------------------------------------------------------------

UPDATE users 
SET full_name = name 
WHERE name IS NOT NULL 
  AND (full_name IS NULL OR full_name = '');

SELECT '✅ Данные перенесены из name в full_name' as status;

-- ПРОВЕРКА РЕЗУЛЬТАТА
-- ----------------------------------------------------------------------------

SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
  AND column_name IN ('name', 'full_name', 'hashed_password', 'email', 'telegram_id', 'whatsapp_number')
ORDER BY column_name;

SELECT '🎉 МИГРАЦИЯ ЗАВЕРШЕНА! Критические ошибки исправлены.' as result; 