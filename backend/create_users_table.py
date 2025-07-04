#!/usr/bin/env python3
"""
Скрипт для создания таблицы пользователей
"""

from backend.database import engine, Base
from backend.models.user import User

def create_users_table():
    """Создает таблицу пользователей"""
    try:
        # Создаем таблицу
        User.__table__.create(bind=engine, checkfirst=True)
        print("✅ Таблица 'users' успешно создана!")
        
        # Показываем структуру таблицы
        print("\n📋 Структура таблицы 'users':")
        print("-" * 50)
        for column in User.__table__.columns:
            print(f"  {column.name:<15} {column.type} {'' if column.nullable else 'NOT NULL'}")
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ Ошибка при создании таблицы: {e}")

if __name__ == "__main__":
    create_users_table() 