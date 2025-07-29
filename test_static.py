#!/usr/bin/env python3
"""
Тест для проверки статических файлов
"""
import requests
import time

def test_static_files():
    """Тестирует доступность основных статических файлов"""
    base_url = "http://localhost:8002"
    
    # Список файлов для тестирования
    static_files = [
        "/css/style.css",
        "/css/zillow-style.css",
        "/css/bootstrap.min.css",
        "/css/font-awesome.min.css",
        "/js/jquery.min.js",
        "/js/bootstrap.bundle.min.js",
        "/static/css/style.css",
        "/static/js/jquery.min.js",
        "/locales/ru.json",
        "/locales/en.json"
    ]
    
    print("🧪 Тестирование статических файлов...")
    print("=" * 50)
    
    for file_path in static_files:
        try:
            response = requests.get(f"{base_url}{file_path}", timeout=5)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {file_path} - {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {file_path} - Ошибка: {e}")
    
    print("=" * 50)
    print("Тест завершен!")

if __name__ == "__main__":
    # Ждем немного, чтобы сервер запустился
    print("⏳ Ждем запуска сервера...")
    time.sleep(3)
    test_static_files() 