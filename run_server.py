#!/usr/bin/env python3
"""
🚀 Скрипт запуска сервера Sianoro
Автоматически настраивает PYTHONPATH и запускает сервер
"""

import os
import sys
from pathlib import Path

# Добавляем папку backend в PYTHONPATH
project_root = Path(__file__).resolve().parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

# Переходим в папку backend для корректной работы
os.chdir(backend_path)

# Импортируем и запускаем сервер
if __name__ == "__main__":
    print("🚀 Запуск сервера Sianoro...")
    print(f"📁 Рабочая директория: {os.getcwd()}")
    print(f"🐍 Python PATH: {sys.path[0]}")
    print("📍 Админка: http://localhost:8002/admin")
    print("🏠 Управление арендой: http://localhost:8002/admin/rental")
    print("🏗️ Добавить новостройку: http://localhost:8002/admin/add-project")
    print("=" * 50)
    
    try:
        import uvicorn
        # Проверяем, что main.py существует
        if not (Path("main.py").exists()):
            print("❌ Файл main.py не найден в директории backend")
            sys.exit(1)
        
        # Запускаем сервер с правильным импортом
        uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("💡 Установите зависимости: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        sys.exit(1) 