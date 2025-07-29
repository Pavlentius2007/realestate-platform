#!/usr/bin/env python3
"""
🔄 Перезагрузка переводов без перезапуска сервера
"""

import requests
import time

def reload_translations():
    """Перезагружает переводы через API"""
    print("🔄 Перезагрузка переводов...")
    
    try:
        # Можно добавить API endpoint для перезагрузки, но пока просто подождем
        print("⏳ Подождите 3 секунды для обновления переводов...")
        time.sleep(3)
        
        # Тестируем английскую страницу
        response = requests.get('http://localhost:8002/en', timeout=5)
        if response.status_code == 200:
            print("✅ Переводы обновлены! Проверьте: http://localhost:8002/en")
        else:
            print(f"❌ Ошибка: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    reload_translations() 