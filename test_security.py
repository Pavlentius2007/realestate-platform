#!/usr/bin/env python3

"""
Тестирование системы безопасности - санитизация и защита от атак
"""

import requests
import json
import time
from pathlib import Path


def test_security_system():
    """Тестирование системы безопасности"""
    
    print("🧪 Тестирование системы безопасности...")
    
    base_url = "http://localhost:8002"
    
    # 1. Тест XSS защиты
    print("\n1. Тестирование XSS защиты...")
    
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src='javascript:alert(\"XSS\")'></iframe>",
        "<svg onload=alert('XSS')>",
        "<body onload=alert('XSS')>",
        "<input onfocus=alert('XSS') autofocus>",
        "<select onfocus=alert('XSS') autofocus>",
        "<textarea onfocus=alert('XSS') autofocus>",
        "<keygen onfocus=alert('XSS') autofocus>",
        "<video><source onerror=alert('XSS')>",
        "<audio src=x onerror=alert('XSS')>",
        "<details open ontoggle=alert('XSS')>",
        "<marquee onstart=alert('XSS')>",
        "<style>@import'javascript:alert(\"XSS\")';</style>"
    ]
    
    for i, payload in enumerate(xss_payloads):
        try:
            # Тест через JSON API
            response = requests.post(
                f"{base_url}/api/auth/register",
                json={
                    "username": f"test_user_{i}",
                    "email": f"test{i}@example.com",
                    "password": "test123",
                    "full_name": payload  # XSS payload в имени
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"   XSS тест {i+1}: {response.status_code} - {payload[:50]}...")
            
            if response.status_code == 400:
                print(f"   ✅ XSS атака заблокирована")
            elif response.status_code == 200:
                print(f"   ⚠️ XSS атака прошла (возможно санитизирована)")
            else:
                print(f"   ❓ Неожиданный статус: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Ошибка XSS теста {i+1}: {e}")
        
        time.sleep(0.1)
    
    # 2. Тест SQL инъекций
    print("\n2. Тестирование защиты от SQL инъекций...")
    
    sql_payloads = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "' UNION SELECT * FROM users --",
        "admin'--",
        "admin' /*",
        "' OR 1=1#",
        "' OR 'a'='a",
        "') OR ('1'='1",
        "' OR '1'='1' /*",
        "1' OR '1'='1",
        "'; INSERT INTO users VALUES ('hacker', 'password'); --",
        "' OR EXISTS(SELECT * FROM users WHERE username='admin') --",
        "' AND (SELECT COUNT(*) FROM users) > 0 --",
        "'; EXEC xp_cmdshell('dir'); --",
        "' UNION SELECT username, password FROM users --"
    ]
    
    for i, payload in enumerate(sql_payloads):
        try:
            # Тест через form data
            response = requests.post(
                f"{base_url}/api/auth/login",
                data={
                    "username": payload,  # SQL injection в username
                    "password": "test123"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            
            print(f"   SQL тест {i+1}: {response.status_code} - {payload[:50]}...")
            
            if response.status_code == 400:
                print(f"   ✅ SQL инъекция заблокирована")
            elif response.status_code == 401:
                print(f"   ✅ SQL инъекция не сработала (неверные данные)")
            elif response.status_code == 200:
                print(f"   ⚠️ SQL инъекция возможно прошла")
            else:
                print(f"   ❓ Неожиданный статус: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Ошибка SQL теста {i+1}: {e}")
        
        time.sleep(0.1)
    
    # 3. Тест санитизации query параметров
    print("\n3. Тестирование санитизации query параметров...")
    
    dangerous_queries = [
        {"search": "<script>alert('XSS')</script>"},
        {"filter": "'; DROP TABLE properties; --"},
        {"sort": "<img src=x onerror=alert('XSS')>"},
        {"page": "javascript:alert('XSS')"},
        {"limit": "' OR '1'='1"}
    ]
    
    for i, query_params in enumerate(dangerous_queries):
        try:
            response = requests.get(
                f"{base_url}/ru/properties",
                params=query_params,
                timeout=10
            )
            
            print(f"   Query тест {i+1}: {response.status_code} - {list(query_params.values())[0][:50]}...")
            
            if response.status_code == 400:
                print(f"   ✅ Опасный query заблокирован")
            elif response.status_code == 200:
                print(f"   ⚠️ Query прошел (возможно санитизирован)")
            else:
                print(f"   ❓ Неожиданный статус: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Ошибка Query теста {i+1}: {e}")
        
        time.sleep(0.1)
    
    # 4. Тест multipart данных
    print("\n4. Тестирование multipart данных...")
    
    try:
        # Создаем тестовый файл
        test_file_content = "<script>alert('XSS')</script>"
        
        files = {
            'file': ('test.txt', test_file_content, 'text/plain')
        }
        
        data = {
            'title': "<script>alert('XSS')</script>",
            'description': "'; DROP TABLE properties; --",
            'price': "1000"
        }
        
        response = requests.post(
            f"{base_url}/admin/add-property",
            files=files,
            data=data,
            timeout=10
        )
        
        print(f"   Multipart тест: {response.status_code}")
        
        if response.status_code == 400:
            print(f"   ✅ Multipart атака заблокирована")
        elif response.status_code in [200, 302]:
            print(f"   ⚠️ Multipart прошел (возможно санитизирован)")
        else:
            print(f"   ❓ Неожиданный статус: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Ошибка Multipart теста: {e}")
    
    # 5. Проверка логов безопасности
    print("\n5. Проверка логов безопасности...")
    
    try:
        logs_dir = Path("logs")
        if logs_dir.exists():
            security_log = logs_dir / "security.log"
            if security_log.exists():
                with open(security_log, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    recent_lines = lines[-10:]  # Последние 10 записей
                    
                print(f"   📊 Найдено {len(lines)} записей в security.log")
                print("   📋 Последние записи:")
                
                for line in recent_lines:
                    if line.strip():
                        try:
                            log_entry = json.loads(line)
                            timestamp = log_entry.get('timestamp', '')[:19]
                            message = log_entry.get('message', '')
                            print(f"   {timestamp}: {message}")
                        except:
                            print(f"   {line.strip()}")
            else:
                print("   ❌ Файл security.log не найден")
        else:
            print("   ❌ Директория logs не найдена")
            
    except Exception as e:
        print(f"   ❌ Ошибка чтения логов: {e}")
    
    print("\n✅ Тестирование системы безопасности завершено!")


if __name__ == "__main__":
    test_security_system() 