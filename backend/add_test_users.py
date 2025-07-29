#!/usr/bin/env python3
"""
Скрипт для добавления тестовых пользователей
"""

from backend.database import SessionLocal
from backend.models.user import User
from datetime import datetime, timedelta
import random

def add_test_users():
    """Добавляет тестовых пользователей"""
    db = SessionLocal()
    
    try:
        # Тестовые пользователи
        test_users = [
            {
                'name': 'Анна Николаева',
                'email': 'anna.nikolaeva@mail.ru',
                'phone': '+7 925 123 4567',
                'whatsapp': '+66 81 234 5678',
                'telegram': '@anna_thailand',
                'instagram': '@anna_pattaya',
                'city': 'Москва',
                'country': 'Россия',
                'budget_min': 3000000,
                'budget_max': 5000000,
                'property_type': 'condo',
                'source': 'website',
                'notes': 'Ищет кондо с видом на море, рассматривает Джомтьен. Планирует покупку до конца года.',
                'status': 'interested',
                'priority': 'high'
            },
            {
                'name': 'Михаил Петров',
                'email': 'mikhail.petrov@gmail.com',
                'phone': '+7 909 876 5432',
                'whatsapp': '+66 82 345 6789',
                'telegram': '@mike_thailand',
                'city': 'Санкт-Петербург',
                'country': 'Россия',
                'budget_min': 5000000,
                'budget_max': 8000000,
                'property_type': 'villa',
                'source': 'referral',
                'notes': 'Рекомендация от клиента Анны. Интересуется виллами в районе Центральной Паттайи.',
                'status': 'contacted',
                'priority': 'high'
            },
            {
                'name': 'Елена Смирнова',
                'email': 'elena.smirnova@yandex.ru',
                'phone': '+7 916 555 7777',
                'whatsapp': '+66 83 456 7890',
                'instagram': '@elena_travels',
                'city': 'Екатеринбург',
                'country': 'Россия',
                'budget_min': 2000000,
                'budget_max': 3500000,
                'property_type': 'studio',
                'source': 'social',
                'notes': 'Молодая семья, ищут студию или 1-комнатную для отдыха и сдачи в аренду.',
                'status': 'new',
                'priority': 'medium'
            },
            {
                'name': 'Дмитрий Козлов',
                'email': 'dmitry.kozlov@outlook.com',
                'phone': '+7 917 888 9999',
                'telegram': '@dmitry_invest',
                'city': 'Казань',
                'country': 'Россия',
                'budget_min': 1500000,
                'budget_max': 2500000,
                'property_type': 'condo',
                'source': 'advertising',
                'notes': 'Инвестор, рассматривает несколько объектов для сдачи в аренду туристам.',
                'status': 'contacted',
                'priority': 'medium'
            },
            {
                'name': 'Ольга Волкова',
                'email': 'olga.volkova@bk.ru',
                'phone': '+7 926 111 2222',
                'whatsapp': '+66 84 567 8901',
                'telegram': '@olga_pattaya',
                'instagram': '@olga_lifestyle',
                'city': 'Новосибирск',
                'country': 'Россия',
                'budget_min': 4000000,
                'budget_max': 7000000,
                'property_type': 'penthouse',
                'source': 'website',
                'notes': 'VIP клиент, ищет пентхаус с террасой. Готова к быстрой сделке при подходящем варианте.',
                'status': 'interested',
                'priority': 'high'
            },
            {
                'name': 'John Smith',
                'email': 'john.smith@gmail.com',
                'phone': '+1 555 123 4567',
                'whatsapp': '+66 85 678 9012',
                'telegram': '@john_thailand',
                'city': 'New York',
                'country': 'USA',
                'budget_min': 4000000,
                'budget_max': 6000000,
                'property_type': 'villa',
                'source': 'referral',
                'notes': 'American expat working in Bangkok. Looking for vacation home in Pattaya.',
                'status': 'new',
                'priority': 'medium'
            }
        ]
        
        # Добавляем пользователей
        for user_data in test_users:
            # Случайная дата создания (последние 30 дней)
            days_ago = random.randint(0, 30)
            created_at = datetime.utcnow() - timedelta(days=days_ago)
            
            # Случайная дата последнего контакта для некоторых пользователей
            last_contact = None
            if user_data['status'] in ['contacted', 'interested']:
                contact_days_ago = random.randint(1, days_ago or 1)
                last_contact = datetime.utcnow() - timedelta(days=contact_days_ago)
            
            user = User(
                name=user_data['name'],
                email=user_data.get('email'),
                phone=user_data.get('phone'),
                whatsapp=user_data.get('whatsapp'),
                telegram=user_data.get('telegram'),
                instagram=user_data.get('instagram'),
                city=user_data.get('city'),
                country=user_data.get('country'),
                budget_min=user_data.get('budget_min'),
                budget_max=user_data.get('budget_max'),
                property_type=user_data.get('property_type'),
                source=user_data.get('source'),
                notes=user_data.get('notes'),
                status=user_data.get('status', 'new'),
                priority=user_data.get('priority', 'medium'),
                is_active=True,
                created_at=created_at,
                last_contact=last_contact
            )
            
            db.add(user)
        
        db.commit()
        print(f"✅ Добавлено {len(test_users)} тестовых пользователей!")
        
        # Показываем результат
        all_users = db.query(User).all()
        print(f"\n📊 Всего пользователей в базе: {len(all_users)}")
        print("\n👥 Добавленные пользователи:")
        print("-" * 60)
        for user in test_users:
            print(f"  {user['name']:<20} | {user['status']:<12} | {user['priority']}")
        print("-" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при добавлении пользователей: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_test_users() 