#!/usr/bin/env python3
"""
Тестовый скрипт для проверки Rate Limiting
"""

import requests
import time
import json

BASE_URL = "http://localhost:8002"

def test_rate_limiting():
    """Тестирует Rate Limiting"""
    print("🚦 Тестирование Rate Limiting...")
    
    # Тест 1: Нормальные запросы
    print("\n1. Нормальные запросы:")
    try:
        response = requests.get(f"{BASE_URL}/ru", timeout=5)
        print(f"   Статус: {response.status_code}")
        
        # Проверяем заголовки rate limit
        headers = response.headers
        if "X-RateLimit-Limit" in headers:
            print(f"   ✅ Rate Limit Headers найдены:")
            print(f"   - Limit: {headers.get('X-RateLimit-Limit')}")
            print(f"   - Remaining: {headers.get('X-RateLimit-Remaining')}")
            print(f"   - Reset: {headers.get('X-RateLimit-Reset')}")
        else:
            print("   ❌ Rate Limit Headers не найдены")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Тест 2: Быстрые запросы для превышения лимита
    print("\n2. Быстрые запросы (тест burst protection):")
    try:
        success_count = 0
        rate_limited_count = 0
        
        for i in range(25):  # Больше чем burst limit (20)
            response = requests.get(f"{BASE_URL}/ru", timeout=2)
            
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                rate_limited_count += 1
                print(f"   📊 Запрос {i+1}: Rate Limited (429)")
                break
            
            time.sleep(0.1)  # Короткая пауза
        
        print(f"   ✅ Успешных запросов: {success_count}")
        print(f"   🚫 Rate limited запросов: {rate_limited_count}")
        
        if rate_limited_count > 0:
            print("   ✅ Burst protection работает!")
        else:
            print("   ❌ Burst protection не сработал")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Тест 3: API endpoints
    print("\n3. API endpoints:")
    try:
        # Тестируем API endpoint
        response = requests.get(f"{BASE_URL}/api/auth/login-page", timeout=5)
        print(f"   API auth статус: {response.status_code}")
        
        # Проверяем заголовки
        headers = response.headers
        if "X-RateLimit-Limit" in headers:
            print(f"   ✅ API Rate Limit Headers:")
            print(f"   - Limit: {headers.get('X-RateLimit-Limit')}")
            print(f"   - Remaining: {headers.get('X-RateLimit-Remaining')}")
        else:
            print("   ❌ API Rate Limit Headers не найдены")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Тест 4: Статические файлы (должны быть exempt)
    print("\n4. Статические файлы (должны быть exempt):")
    try:
        response = requests.get(f"{BASE_URL}/static/css/style.css", timeout=5)
        print(f"   Статический файл статус: {response.status_code}")
        
        # Статические файлы не должны иметь rate limit headers
        if "X-RateLimit-Limit" not in response.headers:
            print("   ✅ Статические файлы exempt от rate limiting")
        else:
            print("   ❌ Статические файлы не exempt от rate limiting")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")

if __name__ == "__main__":
    test_rate_limiting() 