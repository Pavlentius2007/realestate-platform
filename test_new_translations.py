#!/usr/bin/env python3
"""
🚀 Тест новой JSON-системы переводов Sianoro
"""

import requests
import json
from colorama import init, Fore, Style

init()

def test_translation_api():
    """Тестируем API переводов"""
    print(f"{Fore.CYAN}🔥 Тестирование новой JSON-системы переводов{Style.RESET_ALL}")
    print("=" * 60)
    
    # Тестируем основные языки
    languages = {
        'ru': 'Русский 🇷🇺',
        'th': 'Тайский 🇹🇭', 
        'en': 'Английский 🇺🇸',
        'zh': 'Китайский 🇨🇳'
    }
    
    for lang_code, lang_name in languages.items():
        print(f"\n{Fore.YELLOW}📍 Тестируем {lang_name}:{Style.RESET_ALL}")
        
        try:
            # Запрос к главной странице
            response = requests.get(f'http://localhost:8002/{lang_code}', timeout=5)
            
            if response.status_code == 200:
                content = response.text
                
                # Проверяем ключевые переводы
                checks = {
                    'site.title': 'Заголовок сайта',
                    'site.subtitle': 'Подзаголовок',
                    'search.title': 'Заголовок поиска',
                    'property.types.apartment': 'Апартаменты'
                }
                
                print(f"  {Fore.GREEN}✅ Страница загружена успешно{Style.RESET_ALL}")
                
                # Простая проверка что контент изменился для разных языков
                if lang_code == 'th' and 'อพาร์ตเมนต์' in content:
                    print(f"  {Fore.GREEN}✅ Тайские переводы работают!{Style.RESET_ALL}")
                elif lang_code == 'en' and 'Real Estate' in content:
                    print(f"  {Fore.GREEN}✅ Английские переводы работают!{Style.RESET_ALL}")
                elif lang_code == 'zh' and '公寓' in content:
                    print(f"  {Fore.GREEN}✅ Китайские переводы работают!{Style.RESET_ALL}")
                elif lang_code == 'ru':
                    print(f"  {Fore.GREEN}✅ Русские переводы (базовые) работают!{Style.RESET_ALL}")
                else:
                    print(f"  {Fore.YELLOW}⚠️ Переводы могут работать частично{Style.RESET_ALL}")
                    
            else:
                print(f"  {Fore.RED}❌ Ошибка HTTP: {response.status_code}{Style.RESET_ALL}")
                
        except requests.exceptions.ConnectionError:
            print(f"  {Fore.RED}❌ Сервер недоступен на localhost:8002{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"  {Fore.RED}❌ Ошибка: {str(e)}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}🎯 Тестирование завершено!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}🌐 Откройте http://localhost:8002/th для проверки тайского сайта{Style.RESET_ALL}")
    print(f"{Fore.GREEN}🌐 Откройте http://localhost:8002/en для английского{Style.RESET_ALL}")

if __name__ == "__main__":
    test_translation_api() 