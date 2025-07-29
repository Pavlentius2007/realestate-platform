#!/usr/bin/env python3
"""
🧪 Тестирование работоспособности сервера Sianoro
Проверяет доступность основных роутов
"""

import requests
import sys
from urllib.parse import urljoin

BASE_URL = "http://localhost:8002"

def test_route(route, description):
    """Тестирует доступность роута"""
    try:
        url = urljoin(BASE_URL, route)
        response = requests.get(url, timeout=5)
        status = "✅" if response.status_code == 200 else f"❌ {response.status_code}"
        print(f"{status} {description}: {route}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ {description}: {route} - Ошибка: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование сервера Sianoro...")
    print("=" * 50)
    
    # Проверяем основные роуты
    routes = [
        ("/admin", "Админка"),
        ("/admin/rental", "Управление арендой"),
        ("/admin/add", "Добавить объект"),
        ("/admin/add-project", "Добавить проект"),
        ("/admin/properties", "Список объектов"),
        ("/admin/projects", "Список проектов"),
        ("/ru", "Главная страница"),
        ("/ru/properties/new-builds", "Новостройки"),
        ("/ru/projects", "Проекты"),
    ]
    
    passed = 0
    total = len(routes)
    
    for route, description in routes:
        if test_route(route, description):
            passed += 1
    
    print("=" * 50)
    print(f"📊 Результат: {passed}/{total} роутов работают")
    
    if passed == total:
        print("🎉 Все роуты работают! Сервер запущен корректно.")
        return True
    else:
        print(f"⚠️ {total - passed} роутов не работают.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        sys.exit(1) 