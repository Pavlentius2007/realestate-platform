-- ============================================================================
-- ДОБАВЛЕНИЕ CRM-ПОЛЕЙ В ТАБЛИЦУ USERS
-- Исправляет ошибки формы добавления пользователя в админке
-- Выполните этот скрипт в PGAdmin4 ПОСЛЕ основного исправления БД
-- ============================================================================

-- Добавляем CRM поля для управления клиентами
-- ----------------------------------------------------------------------------

-- Бюджет клиента (минимальный и максимальный)
ALTER TABLE users ADD COLUMN IF NOT EXISTS budget_min INTEGER;
ALTER TABLE users ADD COLUMN IF NOT EXISTS budget_max INTEGER;

-- Локация клиента
ALTER TABLE users ADD COLUMN IF NOT EXISTS city VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS country VARCHAR(255);

-- Предпочтения клиента
ALTER TABLE users ADD COLUMN IF NOT EXISTS property_type VARCHAR(255);

-- CRM поля
ALTER TABLE users ADD COLUMN IF NOT EXISTS notes TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS priority VARCHAR(50) DEFAULT 'medium';
ALTER TABLE users ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'new';

-- Комментарии к полям
-- ----------------------------------------------------------------------------

COMMENT ON COLUMN users.budget_min IS 'Минимальный бюджет клиента в USD';
COMMENT ON COLUMN users.budget_max IS 'Максимальный бюджет клиента в USD';
COMMENT ON COLUMN users.city IS 'Город клиента';
COMMENT ON COLUMN users.country IS 'Страна клиента';
COMMENT ON COLUMN users.property_type IS 'Предпочитаемый тип недвижимости';
COMMENT ON COLUMN users.notes IS 'Заметки менеджера о клиенте';
COMMENT ON COLUMN users.priority IS 'Приоритет лида (low, medium, high)';
COMMENT ON COLUMN users.status IS 'Статус лида (new, contacted, qualified, deal, lost)';

-- Создание индексов для оптимизации
-- ----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_users_budget_range ON users(budget_min, budget_max);
CREATE INDEX IF NOT EXISTS idx_users_location ON users(city, country);
CREATE INDEX IF NOT EXISTS idx_users_property_type ON users(property_type);
CREATE INDEX IF NOT EXISTS idx_users_priority ON users(priority);
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);

-- Проверка результата
-- ----------------------------------------------------------------------------

SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
  AND column_name IN ('budget_min', 'budget_max', 'city', 'country', 'property_type', 'notes', 'priority', 'status')
ORDER BY column_name;

SELECT '✅ CRM поля добавлены в таблицу users! Форма добавления пользователя теперь работает.' as result; 