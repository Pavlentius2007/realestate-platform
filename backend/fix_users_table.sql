-- ============================================================================
-- МИГРАЦИЯ ДЛЯ ТАБЛИЦЫ USERS
-- Приводит структуру таблицы в соответствие с моделью User
-- Выполните этот скрипт через PGAdmin4
-- ============================================================================

-- 1. ДОБАВЛЕНИЕ НЕДОСТАЮЩИХ ПОЛЕЙ
-- ----------------------------------------------------------------------------

-- Добавляем поле hashed_password (если не существует)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255);

-- Добавляем поле full_name (если не существует)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS full_name VARCHAR(255);

-- Добавляем поле email (если не существует)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS email VARCHAR(255);

-- Добавляем поле telegram_id (если не существует)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS telegram_id VARCHAR(255);

-- Добавляем поле whatsapp_number (если не существует)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS whatsapp_number VARCHAR(255);

-- Добавляем поле instagram_id (если не существует)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS instagram_id VARCHAR(255);

-- Добавляем поле source (если не существует)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS source VARCHAR(255);

-- Добавляем поле is_active (если не существует)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- Добавляем поле created_at (если не существует)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- 2. ОБНОВЛЕНИЕ СУЩЕСТВУЮЩИХ ДАННЫХ
-- ----------------------------------------------------------------------------

-- Переносим данные из старых полей (если они существуют)
-- Проверяем существование столбца 'name' и переносим в 'full_name'
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name = 'users' AND column_name = 'name') THEN
        UPDATE users SET full_name = name WHERE full_name IS NULL AND name IS NOT NULL;
    END IF;
END $$;

-- 3. СОЗДАНИЕ ИНДЕКСОВ ДЛЯ ОПТИМИЗАЦИИ
-- ----------------------------------------------------------------------------

-- Индекс для быстрого поиска по email
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Индекс для быстрого поиска по telegram_id
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);

-- Индекс для быстрого поиска по whatsapp_number
CREATE INDEX IF NOT EXISTS idx_users_whatsapp_number ON users(whatsapp_number);

-- Индекс для фильтрации активных пользователей
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Индекс для сортировки по дате создания
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- 4. ДОБАВЛЕНИЕ КОММЕНТАРИЕВ К ПОЛЯМ
-- ----------------------------------------------------------------------------

COMMENT ON COLUMN users.full_name IS 'Полное имя пользователя';
COMMENT ON COLUMN users.email IS 'Email адрес пользователя';
COMMENT ON COLUMN users.hashed_password IS 'Хешированный пароль пользователя';
COMMENT ON COLUMN users.phone IS 'Номер телефона пользователя';
COMMENT ON COLUMN users.telegram_id IS 'ID пользователя в Telegram';
COMMENT ON COLUMN users.whatsapp_number IS 'Номер WhatsApp пользователя';
COMMENT ON COLUMN users.instagram_id IS 'ID пользователя в Instagram';
COMMENT ON COLUMN users.source IS 'Источник регистрации пользователя';
COMMENT ON COLUMN users.is_active IS 'Активен ли пользователь';
COMMENT ON COLUMN users.created_at IS 'Дата и время создания записи';

-- 5. ВЫВОД РЕЗУЛЬТАТА
-- ----------------------------------------------------------------------------

SELECT 'Миграция таблицы users выполнена успешно!' as result; 