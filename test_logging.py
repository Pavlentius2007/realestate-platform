#!/usr/bin/env python3
"""
Тестирование системы централизованного логирования
"""

import requests
import time
import asyncio
from pathlib import Path
import json


def test_logging_system():
    """Тестирование различных типов логирования"""
    
    print("🧪 Тестирование системы логирования...")
    
    base_url = "http://localhost:8002"
    
    # 1. Тест обычных запросов (должны логироваться в access.log)
    print("\n1. Тестирование обычных запросов...")
    
    for i in range(5):
        try:
            response = requests.get(f"{base_url}/ru", timeout=10)
            print(f"   Запрос {i+1}: {response.status_code}")
            time.sleep(0.5)
        except Exception as e:
            print(f"   Запрос {i+1}: Ошибка - {e}")
    
    # 2. Тест аутентификации (должны логироваться в security.log)
    print("\n2. Тестирование аутентификации...")
    
    try:
        # Успешная аутентификация
        response = requests.post(f"{base_url}/api/auth/login", json={
            "username": "test@example.com",
            "password": "testpass123"
        }, timeout=10)
        print(f"   Логин: {response.status_code}")
        
        # Неуспешная аутентификация
        response = requests.post(f"{base_url}/api/auth/login", json={
            "username": "wrong@example.com", 
            "password": "wrongpass"
        }, timeout=10)
        print(f"   Неверный логин: {response.status_code}")
        
    except Exception as e:
        print(f"   Ошибка аутентификации: {e}")
    
    # 3. Тест rate limiting (должны логироваться в security.log)
    print("\n3. Тестирование rate limiting...")
    
    for i in range(25):  # Превышаем лимит
        try:
            response = requests.get(f"{base_url}/ru", timeout=10)
            if response.status_code == 429:
                print(f"   Запрос {i+1}: Rate limit достигнут - {response.status_code}")
                break
            else:
                print(f"   Запрос {i+1}: {response.status_code}")
        except Exception as e:
            print(f"   Запрос {i+1}: Ошибка - {e}")
        time.sleep(0.1)
    
    # 4. Тест ошибок (должны логироваться в errors.log)
    print("\n4. Тестирование обработки ошибок...")
    
    try:
        # Несуществующий endpoint
        response = requests.get(f"{base_url}/nonexistent-endpoint", timeout=10)
        print(f"   404 ошибка: {response.status_code}")
        
        # Несуществующий язык
        response = requests.get(f"{base_url}/xyz", timeout=10)
        print(f"   Неверный язык: {response.status_code}")
        
    except Exception as e:
        print(f"   Ошибка тестирования: {e}")
    
    # 5. Проверка файлов логов
    print("\n5. Проверка созданных файлов логов...")
    
    logs_dir = Path("logs")
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        print(f"   Найдено файлов логов: {len(log_files)}")
        
        for log_file in log_files:
            size = log_file.stat().st_size
            print(f"   📄 {log_file.name}: {size} bytes")
            
            # Показываем последние несколько строк
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"      Последние записи:")
                        for line in lines[-3:]:
                            try:
                                # Пытаемся парсить JSON
                                log_entry = json.loads(line.strip())
                                print(f"        {log_entry.get('timestamp', 'NO_TIME')} - {log_entry.get('level', 'NO_LEVEL')} - {log_entry.get('message', 'NO_MSG')}")
                            except:
                                # Если не JSON, выводим как есть
                                print(f"        {line.strip()}")
                    else:
                        print("      Файл пуст")
            except Exception as e:
                print(f"      Ошибка чтения файла: {e}")
    else:
        print("   ❌ Директория logs не найдена")
    
    print("\n✅ Тестирование завершено!")


if __name__ == "__main__":
    test_logging_system() 