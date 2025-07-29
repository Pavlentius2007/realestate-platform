#!/usr/bin/env python3
"""
📊 Скрипт для добавления полей аренды в БД
Выполняет SQL-скрипт add_rental_fields.sql
"""

import sys
import os
from pathlib import Path

# Добавляем папку backend в PYTHONPATH
project_root = Path(__file__).resolve().parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

# Переходим в папку backend
os.chdir(backend_path)

def run_migration():
    """Выполняет миграцию полей аренды"""
    try:
        from database import engine
        from sqlalchemy import text
        
        # Читаем SQL-скрипт
        sql_file = Path("add_rental_fields.sql")
        if not sql_file.exists():
            print(f"❌ SQL-скрипт не найден: {sql_file}")
            return False
            
        sql_content = sql_file.read_text(encoding='utf-8')
        
        # Выполняем SQL
        with engine.connect() as connection:
            # Разбиваем на отдельные команды
            commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
            
            for i, command in enumerate(commands):
                if command.upper().startswith(('ALTER', 'UPDATE', 'COMMENT', 'CREATE')):
                    try:
                        result = connection.execute(text(command))
                        print(f"✅ Команда {i+1}/{len(commands)} выполнена")
                    except Exception as e:
                        if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                            print(f"⚠️ Команда {i+1}: поле уже существует - пропускаем")
                        else:
                            print(f"❌ Ошибка в команде {i+1}: {e}")
                elif command.upper().startswith('SELECT'):
                    result = connection.execute(text(command))
                    for row in result:
                        print(f"🎉 {row[0]}")
            
            connection.commit()
            
        print("\n✅ Миграция полей аренды завершена!")
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("💡 Убедитесь, что установлены зависимости: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        return False

if __name__ == "__main__":
    print("📊 Миграция полей аренды в БД...")
    print(f"📁 Рабочая директория: {os.getcwd()}")
    print("=" * 50)
    
    success = run_migration()
    sys.exit(0 if success else 1) 