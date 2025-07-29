#!/usr/bin/env python3
"""
Скрипт для пересоздания таблицы пользователей
"""

from backend.database import engine, Base
from backend.models.user import User
from sqlalchemy import text

def recreate_users_table():
    """Пересоздает таблицу пользователей"""
    try:
        print("🔄 Пересоздание таблицы пользователей...")
        
        # Удаляем существующую таблицу
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
            conn.commit()
            print("✅ Старая таблица 'users' удалена")
        
        # Создаем новую таблицу с правильной структурой
        User.__table__.create(bind=engine, checkfirst=True)
        print("✅ Новая таблица 'users' создана!")
        
        # Показываем структуру таблицы
        print("\n📋 Структура новой таблицы 'users':")
        print("-" * 70)
        for column in User.__table__.columns:
            nullable = "" if column.nullable else "NOT NULL"
            print(f"  {column.name:<20} {str(column.type):<25} {nullable}")
        print("-" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при пересоздании таблицы: {e}")
        return False

if __name__ == "__main__":
    recreate_users_table() 