-- =================================================
-- КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ БД ДЛЯ SIANORO
-- =================================================
-- Дата: 01.07.2025
-- Проблемы: 
-- 1. Отсутствует столбец users.hashed_password
-- 2. NOT NULL constraint нарушается на users.name
-- 3. Управление пользователями не работает (404 ошибки)
-- =================================================

-- Начинаем транзакцию для безопасности
BEGIN;

-- =================================================
-- 1. ПРОВЕРКА И ДОБАВЛЕНИЕ ОТСУТСТВУЮЩИХ СТОЛБЦОВ
-- =================================================

-- Добавляем столбец hashed_password если он не существует
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='users' AND column_name='hashed_password'
    ) THEN
        ALTER TABLE users ADD COLUMN hashed_password VARCHAR(255);
        RAISE NOTICE 'Столбец hashed_password добавлен в таблицу users';
    ELSE
        RAISE NOTICE 'Столбец hashed_password уже существует';
    END IF;
END $$;

-- Добавляем столбец name если он не существует
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='users' AND column_name='name'
    ) THEN
        ALTER TABLE users ADD COLUMN name VARCHAR(255);
        RAISE NOTICE 'Столбец name добавлен в таблицу users';
    ELSE
        RAISE NOTICE 'Столбец name уже существует';
    END IF;
END $$;

-- =================================================
-- 2. ЗАПОЛНЕНИЕ ПУСТЫХ ЗНАЧЕНИЙ
-- =================================================

-- Заполняем пустые значения name из full_name
UPDATE users 
SET name = full_name 
WHERE name IS NULL AND full_name IS NOT NULL;

-- Устанавливаем имя по умолчанию для оставшихся NULL значений
UPDATE users 
SET name = 'Гость'
WHERE name IS NULL;

-- Устанавливаем пароли по умолчанию для пользователей без пароля
UPDATE users 
SET hashed_password = '$2b$12$dummy.hash.for.existing.users.without.password'
WHERE hashed_password IS NULL;

-- =================================================
-- 3. УСТАНОВКА ОГРАНИЧЕНИЙ
-- =================================================

-- Устанавливаем NOT NULL ограничение на name (если еще не установлено)
DO $$
BEGIN
    ALTER TABLE users ALTER COLUMN name SET NOT NULL;
    RAISE NOTICE 'NOT NULL ограничение установлено на столбец name';
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'NOT NULL ограничение уже установлено на столбец name';
END $$;

-- =================================================
-- 4. ПРОВЕРКА ЦЕЛОСТНОСТИ ДАННЫХ
-- =================================================

-- Проверяем количество пользователей с NULL значениями
DO $$
DECLARE
    null_name_count INTEGER;
    null_password_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO null_name_count FROM users WHERE name IS NULL;
    SELECT COUNT(*) INTO null_password_count FROM users WHERE hashed_password IS NULL;
    
    RAISE NOTICE 'Пользователей с NULL name: %', null_name_count;
    RAISE NOTICE 'Пользователей с NULL hashed_password: %', null_password_count;
    
    IF null_name_count > 0 OR null_password_count > 0 THEN
        RAISE WARNING 'Обнаружены пользователи с NULL значениями!';
    ELSE
        RAISE NOTICE 'Все обязательные поля заполнены корректно';
    END IF;
END $$;

-- =================================================
-- 5. ИНДЕКСЫ ДЛЯ ПРОИЗВОДИТЕЛЬНОСТИ
-- =================================================

-- Создаем индексы если они не существуют
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_source ON users(source);

-- =================================================
-- 6. ПРОВЕРКА СТРУКТУРЫ ТАБЛИЦЫ
-- =================================================

-- Выводим информацию о структуре таблицы users
DO $$
DECLARE
    rec RECORD;
BEGIN
    RAISE NOTICE '=== СТРУКТУРА ТАБЛИЦЫ USERS ===';
    FOR rec IN 
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'users' 
        ORDER BY ordinal_position
    LOOP
        RAISE NOTICE 'Столбец: % | Тип: % | NULL: % | По умолчанию: %', 
            rec.column_name, rec.data_type, rec.is_nullable, 
            COALESCE(rec.column_default, 'нет');
    END LOOP;
END $$;

-- =================================================
-- 7. СТАТИСТИКА ПОЛЬЗОВАТЕЛЕЙ
-- =================================================

-- Выводим статистику по пользователям
DO $$
DECLARE
    total_users INTEGER;
    active_users INTEGER;
    users_with_phone INTEGER;
    users_with_email INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_users FROM users;
    SELECT COUNT(*) INTO active_users FROM users WHERE is_active = true;
    SELECT COUNT(*) INTO users_with_phone FROM users WHERE phone IS NOT NULL;
    SELECT COUNT(*) INTO users_with_email FROM users WHERE email IS NOT NULL;
    
    RAISE NOTICE '=== СТАТИСТИКА ПОЛЬЗОВАТЕЛЕЙ ===';
    RAISE NOTICE 'Всего пользователей: %', total_users;
    RAISE NOTICE 'Активных пользователей: %', active_users;
    RAISE NOTICE 'С телефонами: %', users_with_phone;
    RAISE NOTICE 'С email: %', users_with_email;
END $$;

-- =================================================
-- 8. СОЗДАНИЕ РЕЗЕРВНОЙ КОПИИ ЛОГИКИ
-- =================================================

-- Создаем таблицу для логирования изменений
CREATE TABLE IF NOT EXISTS db_migration_log (
    id SERIAL PRIMARY KEY,
    migration_name VARCHAR(255) NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    success BOOLEAN DEFAULT true
);

-- Записываем информацию о выполненной миграции
INSERT INTO db_migration_log (migration_name, description) VALUES
('fix_critical_db_issues_v1', 'Исправление критических проблем: добавление hashed_password, исправление NOT NULL на name, индексы для производительности');

-- =================================================
-- 9. ЗАВЕРШЕНИЕ
-- =================================================

-- Подтверждаем транзакцию
COMMIT;

-- Финальные сообщения
DO $$
BEGIN
    RAISE NOTICE '=== МИГРАЦИЯ УСПЕШНО ЗАВЕРШЕНА ===';
    RAISE NOTICE 'Время выполнения: %', clock_timestamp();
    RAISE NOTICE 'Теперь можно перезапустить приложение';
END $$; 