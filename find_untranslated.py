#!/usr/bin/env python3
"""
🔍 Поиск непереведенных строк на английской странице
"""

import requests
import re
from colorama import init, Fore, Style

init()

def find_untranslated():
    """Находит русские слова на английской странице"""
    print(f"{Fore.CYAN}🔍 Поиск непереведенного русского текста{Style.RESET_ALL}")
    print("=" * 60)
    
    try:
        response = requests.get('http://localhost:8002/en', timeout=5)
        
        if response.status_code == 200:
            content = response.text
            
            # Ищем русские слова (кириллица)
            russian_words = re.findall(r'[а-яА-Я]+(?:[а-яА-Я\s]*[а-яА-Я])?', content)
            
            if russian_words:
                print(f"{Fore.RED}❌ Найден русский текст:{Style.RESET_ALL}")
                
                # Убираем дубликаты и сортируем
                unique_words = sorted(set(russian_words))
                
                for word in unique_words:
                    print(f"  🔤 '{word}'")
                
                print(f"\n{Fore.YELLOW}💡 Всего найдено: {len(unique_words)} уникальных русских слов{Style.RESET_ALL}")
                
                # Показываем контекст для первых 3 слов
                print(f"\n{Fore.CYAN}📝 Контекст:{Style.RESET_ALL}")
                for word in unique_words[:3]:
                    # Находим контекст слова
                    start = content.lower().find(word.lower())
                    if start != -1:
                        context_start = max(0, start - 30)
                        context_end = min(len(content), start + len(word) + 30)
                        context = content[context_start:context_end].strip()
                        print(f"  '{word}': ...{context}...")
                        
            else:
                print(f"{Fore.GREEN}✅ Русский текст не найден! Переводы полностью работают.{Style.RESET_ALL}")
                
        else:
            print(f"{Fore.RED}❌ Ошибка HTTP: {response.status_code}{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{Fore.RED}❌ Ошибка: {e}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}🌐 Проверьте сами: http://localhost:8002/en{Style.RESET_ALL}")

if __name__ == "__main__":
    find_untranslated() 