-- Добавление полей для управления арендой в таблицу properties

-- Статус аренды (available, rented, maintenance)
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

-- Обновляем существующие записи
UPDATE properties 
SET rental_status = 'available' 
WHERE rental_status IS NULL;

-- Добавляем комментарии к полям
COMMENT ON COLUMN properties.rental_status IS 'Статус аренды: available, rented, maintenance';
COMMENT ON COLUMN properties.rental_start_date IS 'Дата начала аренды';
COMMENT ON COLUMN properties.rental_end_date IS 'Дата окончания аренды';
COMMENT ON COLUMN properties.renter_name IS 'Имя арендатора';
COMMENT ON COLUMN properties.renter_contact IS 'Контакт арендатора (телефон, email)';
COMMENT ON COLUMN properties.rental_notes IS 'Заметки и комментарии по аренде';

-- Создаем индекс для поиска по статусу аренды
CREATE INDEX IF NOT EXISTS idx_properties_rental_status ON properties(rental_status);

-- Создаем индекс для поиска по датам аренды
CREATE INDEX IF NOT EXISTS idx_properties_rental_dates ON properties(rental_start_date, rental_end_date);

SELECT 'Поля для управления арендой успешно добавлены!' as result; 