-- Добавление поля is_new_building в таблицу properties
-- Выполните этот скрипт в PGAdmin4

ALTER TABLE properties 
ADD COLUMN is_new_building BOOLEAN DEFAULT FALSE;

-- Обновление существующих записей (опционально)
-- Установите флаг новостройки для некоторых объектов
-- UPDATE properties SET is_new_building = TRUE WHERE id IN (1, 2, 3);

-- Создание индекса для оптимизации фильтрации
CREATE INDEX idx_properties_is_new_building ON properties(is_new_building);

-- Комментарий к полю
COMMENT ON COLUMN properties.is_new_building IS 'Флаг новостройки: TRUE - новостройка, FALSE - вторичка'; 