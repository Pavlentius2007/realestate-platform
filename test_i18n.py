#!/usr/bin/env python
"""
Тест-скрипт для проверки работы переключения языков
"""

import requests
import time

def test_language_switching():
    """Тестирует переключение языков на сайте"""
    
    base_url = "http://localhost:8002"
    
    # Проверяем доступность сервера
    try:
        response = requests.get(base_url + "/ru", timeout=5)
        if response.status_code != 200:
            print(f"❌ Сервер недоступен: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Не удалось подключиться к серверу: {e}")
        print("💡 Убедитесь, что сервер запущен на порту 8000")
        return False
    
    print("✅ Сервер доступен")
    
    # Создаем сессию для сохранения cookies
    session = requests.Session()
    
    # Тестируем разные языки
    languages = ['ru', 'en', 'th', 'zh']
    
    for lang in languages:
        print(f"\n🌍 Тестируем язык: {lang}")
        
        try:
            # 1. Переходим на главную страницу с языком
            url = f"{base_url}/{lang}"
            response = session.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"   ✅ Страница /{lang} доступна")
                
                # Проверяем, что язык отображается в HTML
                if f'<span class="uppercase font-medium">{lang}</span>' in response.text:
                    print(f"   ✅ Язык {lang} отображается в интерфейсе")
                else:
                    print(f"   ⚠️  Язык {lang} не найден в HTML")
                
                # Тестируем переключение языка через API
                switch_url = f"{base_url}/lang/{lang}"
                switch_response = session.get(switch_url, timeout=5, allow_redirects=False)
                
                if switch_response.status_code in [302, 200]:
                    print(f"   ✅ API переключения языка работает")
                else:
                    print(f"   ❌ API переключения языка не работает: {switch_response.status_code}")
                    
            else:
                print(f"   ❌ Страница /{lang} недоступна: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Ошибка при тестировании {lang}: {e}")
    
    # Тестируем переводы для всех языков
    test_languages = {
        'en': {
            'name': 'английском', 
            'texts': [
                "Real Estate in Pattaya",
                "Property Search", 
                "Buy",
                "Rent",
                "Smart Search"
            ]
        },
        'th': {
            'name': 'тайском',
            'texts': [
                "อสังหาริมทรัพย์ในพัทยา",  # Недвижимость в Паттайе
                "ค้นหาอสังหาริมทรัพย์",      # Поиск недвижимости  
                "ซื้อ",                     # Купить
                "เช่า",                     # Снять
                "โครงการ"                   # Проекты
            ]
        },
        'zh': {
            'name': 'китайском',
            'texts': [
                "芭提雅房地产",      # Недвижимость в Паттайе
                "房产搜索",         # Поиск недвижимости
                "购买",            # Купить
                "租赁",            # Снять  
                "项目"             # Проекты
            ]
        }
    }
    
    for lang_code, lang_info in test_languages.items():
        print(f"\n🔤 Тестируем переводы на {lang_info['name']}")
        try:
            # Переключаемся на язык
            session.get(f"{base_url}/lang/{lang_code}", timeout=5)
            
            # Загружаем главную страницу
            response = session.get(f"{base_url}/{lang_code}", timeout=5)
            
            if response.status_code == 200:
                # Проверяем наличие переводов
                found_translations = 0
                for text in lang_info['texts']:
                    if text in response.text:
                        print(f"   ✅ Найден перевод: '{text}'")
                        found_translations += 1
                    else:
                        print(f"   ❌ Не найден перевод: '{text}'")
                
                flag = {'en': '🇺🇸', 'th': '🇹🇭', 'zh': '🇨🇳'}[lang_code]
                if found_translations > 0:
                    print(f"   {flag} Найдено {found_translations}/{len(lang_info['texts'])} переводов")
                else:
                    print(f"   ❌ Переводы на {lang_info['name']} не работают")
                    
            else:
                print(f"   ❌ Не удалось загрузить страницу на {lang_info['name']}: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Ошибка при тестировании переводов на {lang_info['name']}: {e}")
    
    print(f"\n🏁 Тестирование завершено")
    return True

if __name__ == "__main__":
    print("🚀 Запуск тестирования переключения языков")
    print("   Ожидание 3 секунды для запуска сервера...")
    time.sleep(3)
    
    test_language_switching() 