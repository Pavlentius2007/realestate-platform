-- ============================================================================
-- ПОЛНАЯ МИГРАЦИЯ ДЛЯ МОДУЛЯ АРЕНДЫ
-- Добавляет все недостающие поля в таблицу properties
-- Выполните этот скрипт через PGAdmin4
-- ============================================================================

-- 1. ДОПОЛНИТЕЛЬНЫЕ ПОЛЯ ДЛЯ ВСЕХ ТИПОВ НЕДВИЖИМОСТИ
-- ----------------------------------------------------------------------------

-- Тип сделки (покупка или аренда)
ALTER TABLE properties 
ADD COLUMN IF NOT EXISTS deal_type VARCHAR(50);

-- Валюта цены
ALTER TABLE properties 
ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT 'THB';

-- Краткое описание
ALTER TABLE properties 
ADD COLUMN IF NOT EXISTS short_description TEXT;

-- Контактный телефон
ALTER TABLE properties 
ADD COLUMN IF NOT EXISTS contact_phone VARCHAR(50);

-- WhatsApp контакт
ALTER TABLE properties 
ADD COLUMN IF NOT EXISTS whatsapp VARCHAR(50);

-- Удобства (строка через запятую)
ALTER TABLE properties 
ADD COLUMN IF NOT EXISTS amenities TEXT;

-- 2. ПОЛЯ ДЛЯ УПРАВЛЕНИЯ АРЕНДОЙ (если еще не добавлены)
-- ----------------------------------------------------------------------------

-- Статус аренды
ALTER TABLE properties 
ADD COLUMN IF NOT EXISTS rental_status VARCHAR(50) DEFAULT 'available';

-- Дата начала аренды
ALTER TABLE properties 
ADD COLUMN IF NOT EXISTS rental_start_date TIMESTAMP;

-- Дата окончания аренды  
ALTER TABLE properties 
ADD COLUMN IF NOT EXISTS rental_end_date TIMESTAMP;

-- Имя арендатора
ALTER TABLE properties 
ADD COLUMN IF NOT EXISTS renter_name VARCHAR(255);

-- Контакт арендатора
ALTER TABLE properties 
ADD COLUMN IF NOT EXISTS renter_contact VARCHAR(255);

-- Заметки по аренде
ALTER TABLE properties 
ADD COLUMN IF NOT EXISTS rental_notes TEXT;

-- 3. УСТАНОВКА ЗНАЧЕНИЙ ПО УМОЛЧАНИЮ
-- ----------------------------------------------------------------------------

-- Устанавливаем тип сделки "buy" для существующих объектов
UPDATE properties 
SET deal_type = 'buy' 
WHERE deal_type IS NULL;

-- Устанавливаем валюту THB для объектов без валюты
UPDATE properties 
SET currency = 'THB' 
WHERE currency IS NULL;

-- Устанавливаем статус аренды "available" для объектов без статуса
UPDATE properties 
SET rental_status = 'available' 
WHERE rental_status IS NULL;

-- 4. СОЗДАНИЕ ИНДЕКСОВ ДЛЯ ОПТИМИЗАЦИИ
-- ----------------------------------------------------------------------------

-- Индекс для поиска по типу сделки
CREATE INDEX IF NOT EXISTS idx_properties_deal_type ON properties(deal_type);

-- Индекс для поиска по статусу аренды
CREATE INDEX IF NOT EXISTS idx_properties_rental_status ON properties(rental_status);

-- Индекс для поиска по датам аренды
CREATE INDEX IF NOT EXISTS idx_properties_rental_dates ON properties(rental_start_date, rental_end_date);

-- Комбинированный индекс для аренды
CREATE INDEX IF NOT EXISTS idx_properties_rent_combo ON properties(deal_type, rental_status) 
WHERE deal_type = 'rent';

-- 5. ДОБАВЛЕНИЕ КОММЕНТАРИЕВ К ПОЛЯМ
-- ----------------------------------------------------------------------------

COMMENT ON COLUMN properties.deal_type IS 'Тип сделки: buy - продажа, rent - аренда';
COMMENT ON COLUMN properties.currency IS 'Валюта цены: THB, USD, EUR, RUB и т.д.';
COMMENT ON COLUMN properties.short_description IS 'Краткое описание объекта для карточек';
COMMENT ON COLUMN properties.contact_phone IS 'Контактный телефон собственника/агента';
COMMENT ON COLUMN properties.whatsapp IS 'WhatsApp контакт для связи';
COMMENT ON COLUMN properties.amenities IS 'Удобства объекта (через запятую)';

COMMENT ON COLUMN properties.rental_status IS 'Статус аренды: available, rented, maintenance';
COMMENT ON COLUMN properties.rental_start_date IS 'Дата начала текущей аренды';
COMMENT ON COLUMN properties.rental_end_date IS 'Дата окончания текущей аренды';
COMMENT ON COLUMN properties.renter_name IS 'Имя текущего арендатора';
COMMENT ON COLUMN properties.renter_contact IS 'Контакт текущего арендатора';
COMMENT ON COLUMN properties.rental_notes IS 'Заметки и комментарии по аренде';

-- 6. ПРОВЕРКА РЕЗУЛЬТАТОВ
-- ----------------------------------------------------------------------------

-- Показываем обновленную структуру таблицы
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'properties'
AND column_name IN (
    'deal_type', 'currency', 'short_description', 'contact_phone', 'whatsapp', 'amenities',
    'rental_status', 'rental_start_date', 'rental_end_date', 'renter_name', 'renter_contact', 'rental_notes'
)
ORDER BY column_name;

-- Проверяем количество объектов по типам
SELECT 
    deal_type,
    COUNT(*) as count,
    COUNT(CASE WHEN rental_status = 'available' THEN 1 END) as available,
    COUNT(CASE WHEN rental_status = 'rented' THEN 1 END) as rented,
    COUNT(CASE WHEN rental_status = 'maintenance' THEN 1 END) as maintenance
FROM properties 
GROUP BY deal_type;

SELECT '🎉 Миграция модуля аренды успешно завершена!' as result; 