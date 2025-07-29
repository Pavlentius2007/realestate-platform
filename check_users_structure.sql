-- Проверка структуры таблицы users
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;

-- Проверка ограничений
SELECT constraint_name, constraint_type 
FROM information_schema.table_constraints 
WHERE table_name = 'users';

-- Показать последние 3 записи для понимания структуры
SELECT * FROM users LIMIT 3; 