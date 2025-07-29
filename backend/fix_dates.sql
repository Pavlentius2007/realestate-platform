-- Исправление дат создания пользователей
-- Выполнить в PGAdmin4 после fix_users_final.sql

-- 1. Установить дату создания для пользователей у которых она NULL
UPDATE users 
SET created_at = CURRENT_TIMESTAMP 
WHERE created_at IS NULL;

-- 2. Установить дату обновления если её нет
UPDATE users 
SET updated_at = CURRENT_TIMESTAMP 
WHERE updated_at IS NULL;

-- 3. Проверить результат
SELECT 
    id, 
    full_name, 
    name,
    created_at, 
    updated_at,
    status
FROM users 
ORDER BY created_at DESC;

-- 4. Показать статистику по датам
SELECT 
    DATE(created_at) as date_created,
    COUNT(*) as users_count
FROM users 
WHERE created_at IS NOT NULL
GROUP BY DATE(created_at) 
ORDER BY date_created DESC; 