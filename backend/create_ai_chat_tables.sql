-- Создание таблиц для ИИ-чата

-- Таблица сессий чата
CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица сообщений чата
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    message_type VARCHAR(50) NOT NULL, -- 'user' или 'assistant'
    content TEXT NOT NULL,
    extra_data JSONB DEFAULT '{}',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_chat_messages_type ON chat_messages(message_type);

-- Комментарии к таблицам
COMMENT ON TABLE chat_sessions IS 'Сессии ИИ-чата для отслеживания предпочтений пользователей';
COMMENT ON TABLE chat_messages IS 'История сообщений в ИИ-чате';

COMMENT ON COLUMN chat_sessions.session_id IS 'Уникальный идентификатор сессии чата';
COMMENT ON COLUMN chat_sessions.user_preferences IS 'JSON с предпочтениями пользователя';
COMMENT ON COLUMN chat_messages.message_type IS 'Тип сообщения: user или assistant';
COMMENT ON COLUMN chat_messages.content IS 'Текст сообщения';
COMMENT ON COLUMN chat_messages.extra_data IS 'Дополнительные данные (параметры поиска, найденные объекты и т.д.)';

-- Функция для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггер для обновления updated_at в chat_sessions
CREATE TRIGGER update_chat_sessions_updated_at 
    BEFORE UPDATE ON chat_sessions 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column(); 