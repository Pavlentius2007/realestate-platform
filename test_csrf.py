#!/usr/bin/env python3
"""
Тестовый скрипт для проверки CSRF защиты
"""

import requests
import json

BASE_URL = "http://localhost:8002"

def test_csrf_protection():
    """Тестирует CSRF защиту"""
    print("🔍 Тестирование CSRF защиты...")
    
    # Тест 1: POST без CSRF токена должен вернуть 403
    print("\n1. POST без CSRF токена:")
    try:
        response = requests.post(
            f"{BASE_URL}/ru/ai-chat",
            data={"message": "Test message"},
            timeout=5
        )
        print(f"   Статус: {response.status_code}")
        if response.status_code == 403:
            print("   ✅ CSRF защита работает!")
        else:
            print(f"   ❌ Ожидался 403, получен {response.status_code}")
            print(f"   Ответ: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Тест 2: Получение CSRF токена
    print("\n2. Получение CSRF токена:")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/login-page", timeout=5)
        print(f"   Статус страницы: {response.status_code}")
        
        # Проверяем наличие CSRF токена в cookie
        csrf_token = response.cookies.get('csrf_token')
        if csrf_token:
            print(f"   ✅ CSRF токен получен: {csrf_token[:20]}...")
        else:
            print("   ❌ CSRF токен не найден в cookies")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Тест 3: API endpoints аутентификации (должны быть exempt)
    print("\n3. API аутентификации (должны быть exempt):")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "test@example.com", "password": "Test123"},
            timeout=5
        )
        print(f"   Статус: {response.status_code}")
        if response.status_code != 403:
            print("   ✅ API аутентификации не заблокирован CSRF")
        else:
            print("   ❌ API аутентификации заблокирован CSRF")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

if __name__ == "__main__":
    test_csrf_protection() 