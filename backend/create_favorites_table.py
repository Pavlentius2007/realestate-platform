#!/usr/bin/env python3

from sqlalchemy import create_engine, text
from backend.database import SQLALCHEMY_DATABASE_URL

def create_favorites_table():
    """Создание таблицы favorites в базе данных"""
    
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    try:
        with engine.begin() as connection:
            # SQL для создания таблицы favorites
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS favorites (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                property_id INTEGER NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(session_id, property_id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_favorites_session_id ON favorites(session_id);
            CREATE INDEX IF NOT EXISTS idx_favorites_property_id ON favorites(property_id);
            CREATE INDEX IF NOT EXISTS idx_favorites_created_at ON favorites(created_at);
            """
            
            connection.execute(text(create_table_sql))
            print("✅ Таблица favorites успешно создана!")
            
    except Exception as e:
        print(f"❌ Ошибка при создании таблицы favorites: {e}")
    finally:
        engine.dispose()

if __name__ == "__main__":
    create_favorites_table() 