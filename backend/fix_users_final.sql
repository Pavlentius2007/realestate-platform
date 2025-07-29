-- Финальное исправление структуры таблицы users
-- Выполнить в PGAdmin4

-- 1. Добавляем недостающий столбец hashed_password, если его нет
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'hashed_password'
    ) THEN
        ALTER TABLE users ADD COLUMN hashed_password VARCHAR;
        RAISE NOTICE 'Столбец hashed_password добавлен';
    ELSE
        RAISE NOTICE 'Столбец hashed_password уже существует';
    END IF;
END
$$;

-- 2. Убираем ограничение NOT NULL с поля name, если оно есть
DO $$
BEGIN
    ALTER TABLE users ALTER COLUMN name DROP NOT NULL;
    RAISE NOTICE 'Ограничение NOT NULL убрано с поля name';
EXCEPTION
    WHEN undefined_column THEN
        RAISE NOTICE 'Столбец name не существует';
    WHEN others THEN
        RAISE NOTICE 'Ограничение NOT NULL уже отсутствует';
END
$$;

-- 3. Добавляем поле last_contact, если его нет
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'last_contact'
    ) THEN
        ALTER TABLE users ADD COLUMN last_contact TIMESTAMP WITH TIME ZONE;
        RAISE NOTICE 'Столбец last_contact добавлен';
    ELSE
        RAISE NOTICE 'Столбец last_contact уже существует';
    END IF;
END
$$;

-- 4. Изменяем тип поля is_active на BOOLEAN, если нужно
DO $$
BEGIN
    -- Сначала попробуем изменить тип
    ALTER TABLE users ALTER COLUMN is_active TYPE BOOLEAN USING 
    CASE 
        WHEN is_active = 't' OR is_active = 'true' OR is_active = '1' THEN TRUE
        WHEN is_active = 'f' OR is_active = 'false' OR is_active = '0' THEN FALSE
        ELSE NULL
    END;
    RAISE NOTICE 'Поле is_active изменено на BOOLEAN';
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'Поле is_active уже имеет тип BOOLEAN или произошла ошибка: %', SQLERRM;
END
$$;

-- 5. Проверяем итоговую структуру
SELECT 'ИТОГОВАЯ СТРУКТУРА ТАБЛИЦЫ USERS:' as info;
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position; 