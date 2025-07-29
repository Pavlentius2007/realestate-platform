#!/usr/bin/env python3
"""
🇺🇸 Тест английских переводов
"""

import requests
import time
from colorama import init, Fore, Style

init()

def test_english_translations():
    """Тестируем английские переводы"""
    print(f"{Fore.CYAN}🇺🇸 Тестирование английских переводов{Style.RESET_ALL}")
    print("=" * 60)
    
    # Ждем запуска сервера
    print("⏳ Ожидание запуска сервера...")
    time.sleep(5)
    
    try:
        response = requests.get('http://localhost:8002/en', timeout=10)
        
        if response.status_code == 200:
            content = response.text
            print(f"{Fore.GREEN}✅ Английская страница загружена{Style.RESET_ALL}")
            
            # Проверяем ключевые английские переводы
            checks = {
                'Real Estate in Pattaya': 'Заголовок сайта',
                'Find the perfect property': 'Подзаголовок',
                'Property Search': 'Заголовок поиска',
                'Choose search type': 'Подзаголовок поиска',
                'Buy': 'Кнопка покупки',
                'Rent': 'Кнопка аренды',
                'Smart Search': 'Умный поиск',
                'Any type': 'Любой тип',
                'Apartments': 'Апартаменты'
            }
            
            found_translations = 0
            for english_text, description in checks.items():
                if english_text in content:
                    print(f"  {Fore.GREEN}✅ {description}: {english_text}{Style.RESET_ALL}")
                    found_translations += 1
                else:
                    print(f"  {Fore.RED}❌ {description}: НЕ НАЙДЕН{Style.RESET_ALL}")
            
            if found_translations >= 6:
                print(f"\n{Fore.GREEN}🎉 ПЕРЕВОДЫ РАБОТАЮТ! Найдено {found_translations}/{len(checks)} переводов{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}⚠️ Частичная работа: {found_translations}/{len(checks)} переводов{Style.RESET_ALL}")
                
            # Проверяем что НЕТ русского текста на английской странице
            russian_words = ['Недвижимость', 'Паттайе', 'Поиск недвижимости', 'Купить']
            russian_found = any(word in content for word in russian_words)
            
            if not russian_found:
                print(f"{Fore.GREEN}✅ Русский текст отсутствует на английской версии{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Обнаружен русский текст на английской странице{Style.RESET_ALL}")
                
        else:
            print(f"{Fore.RED}❌ Ошибка HTTP: {response.status_code}{Style.RESET_ALL}")
            
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}❌ Сервер недоступен. Убедитесь что сервер запущен на localhost:8002{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Ошибка: {str(e)}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}🌐 Проверьте сами: http://localhost:8002/en{Style.RESET_ALL}")

if __name__ == "__main__":
    test_english_translations() 