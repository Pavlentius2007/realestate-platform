"""
Тестовые данные для фикстур
"""

import pytest
from typing import Dict, Any, List
from datetime import datetime, timedelta


@pytest.fixture
def sample_users() -> List[Dict[str, Any]]:
    """Тестовые пользователи"""
    return [
        {
            "username": "testuser1",
            "email": "user1@example.com",
            "password": "password123",
            "full_name": "Test User 1",
            "phone": "+1234567890",
            "role": "user",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "username": "testuser2",
            "email": "user2@example.com",
            "password": "password456",
            "full_name": "Test User 2",
            "phone": "+1234567891",
            "role": "user",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123",
            "full_name": "Admin User",
            "phone": "+1234567892",
            "role": "admin",
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]


@pytest.fixture
def sample_properties() -> List[Dict[str, Any]]:
    """Тестовые объекты недвижимости"""
    return [
        {
            "title": "Современная квартира в центре",
            "description": "Просторная квартира с современным ремонтом",
            "price": 150000,
            "currency": "USD",
            "property_type": "apartment",
            "bedrooms": 2,
            "bathrooms": 1,
            "area": 75.5,
            "floor": 5,
            "total_floors": 10,
            "district": "Центральный",
            "address": "ул. Главная, 123",
            "furnished": True,
            "parking": True,
            "balcony": True,
            "elevator": True,
            "air_conditioning": True,
            "internet": True,
            "status": "active",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "title": "Дом с участком",
            "description": "Уютный дом с большим участком",
            "price": 350000,
            "currency": "USD",
            "property_type": "house",
            "bedrooms": 3,
            "bathrooms": 2,
            "area": 120.0,
            "floor": 1,
            "total_floors": 2,
            "district": "Пригород",
            "address": "ул. Садовая, 45",
            "furnished": False,
            "parking": True,
            "balcony": False,
            "elevator": False,
            "air_conditioning": True,
            "internet": True,
            "status": "active",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "title": "Студия для инвестиций",
            "description": "Компактная студия в новостройке",
            "price": 80000,
            "currency": "USD",
            "property_type": "studio",
            "bedrooms": 0,
            "bathrooms": 1,
            "area": 35.0,
            "floor": 3,
            "total_floors": 15,
            "district": "Новый район",
            "address": "ул. Молодежная, 78",
            "furnished": True,
            "parking": False,
            "balcony": True,
            "elevator": True,
            "air_conditioning": True,
            "internet": True,
            "status": "active",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]


@pytest.fixture
def sample_rental_properties() -> List[Dict[str, Any]]:
    """Тестовые объекты аренды"""
    return [
        {
            "title": "Квартира для аренды",
            "description": "Уютная квартира для долгосрочной аренды",
            "price": 1200,
            "currency": "USD",
            "property_type": "apartment",
            "bedrooms": 1,
            "bathrooms": 1,
            "area": 45.0,
            "floor": 4,
            "total_floors": 9,
            "district": "Центральный",
            "address": "ул. Арендная, 12",
            "furnished": True,
            "parking": True,
            "balcony": True,
            "elevator": True,
            "air_conditioning": True,
            "internet": True,
            "rental_type": "long_term",
            "min_rental_period": 6,
            "pets_allowed": False,
            "status": "active",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]


@pytest.fixture
def sample_projects() -> List[Dict[str, Any]]:
    """Тестовые проекты"""
    return [
        {
            "name": "Zenith Tower",
            "slug": "zenith-tower",
            "description": "Элитный жилой комплекс",
            "developer": "Zenith Development",
            "location": "Центральный район",
            "completion_date": datetime.now() + timedelta(days=365),
            "total_units": 150,
            "price_from": 200000,
            "price_to": 500000,
            "currency": "USD",
            "status": "construction",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "name": "Marina Bay",
            "slug": "marina-bay",
            "description": "Жилой комплекс у моря",
            "developer": "Marina Development",
            "location": "Приморский район",
            "completion_date": datetime.now() + timedelta(days=180),
            "total_units": 80,
            "price_from": 150000,
            "price_to": 400000,
            "currency": "USD",
            "status": "construction",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]


@pytest.fixture
def sample_articles() -> List[Dict[str, Any]]:
    """Тестовые статьи"""
    return [
        {
            "title": "Как выбрать недвижимость в Таиланде",
            "slug": "kak-vybrat-nedvizhimost-v-tailande",
            "content": "# Как выбрать недвижимость в Таиланде\n\nПолное руководство...",
            "excerpt": "Руководство по выбору недвижимости",
            "author": "Sianoro Team",
            "published": True,
            "published_at": datetime.now(),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "title": "Налоги для иностранцев в Таиланде",
            "slug": "nalogi-dlya-inostrancev-v-tailande",
            "content": "# Налоги для иностранцев в Таиланде\n\nПодробная информация...",
            "excerpt": "Информация о налогах",
            "author": "Sianoro Team",
            "published": True,
            "published_at": datetime.now(),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]


@pytest.fixture
def sample_favorites() -> List[Dict[str, Any]]:
    """Тестовые избранные"""
    return [
        {
            "user_id": 1,
            "property_id": 1,
            "created_at": datetime.now()
        },
        {
            "user_id": 1,
            "property_id": 2,
            "created_at": datetime.now()
        }
    ]


@pytest.fixture
def sample_rental_requests() -> List[Dict[str, Any]]:
    """Тестовые заявки на аренду"""
    return [
        {
            "name": "Иван Петров",
            "email": "ivan@example.com",
            "phone": "+1234567890",
            "property_id": 1,
            "message": "Интересует аренда квартиры",
            "check_in_date": datetime.now() + timedelta(days=30),
            "check_out_date": datetime.now() + timedelta(days=90),
            "guests": 2,
            "status": "pending",
            "created_at": datetime.now()
        }
    ]


@pytest.fixture
def sample_ai_chat_messages() -> List[Dict[str, Any]]:
    """Тестовые сообщения AI чата"""
    return [
        {
            "session_id": "test_session_1",
            "user_message": "Помогите найти квартиру в центре",
            "ai_response": "Конечно! Вот несколько вариантов в центре...",
            "created_at": datetime.now()
        },
        {
            "session_id": "test_session_1",
            "user_message": "Какая цена?",
            "ai_response": "Цены варьируются от 100,000 до 300,000 USD...",
            "created_at": datetime.now()
        }
    ]


@pytest.fixture
def sample_search_queries() -> List[Dict[str, Any]]:
    """Тестовые поисковые запросы"""
    return [
        {
            "query": "квартира центр",
            "filters": {
                "property_type": "apartment",
                "district": "Центральный",
                "price_min": 100000,
                "price_max": 200000
            },
            "results_count": 5,
            "created_at": datetime.now()
        },
        {
            "query": "дом участок",
            "filters": {
                "property_type": "house",
                "area_min": 100,
                "price_min": 300000
            },
            "results_count": 2,
            "created_at": datetime.now()
        }
    ]


@pytest.fixture
def sample_analytics_data() -> Dict[str, Any]:
    """Тестовые данные аналитики"""
    return {
        "page_views": [
            {"page": "/", "views": 150, "date": datetime.now().date()},
            {"page": "/properties", "views": 89, "date": datetime.now().date()},
            {"page": "/projects", "views": 45, "date": datetime.now().date()}
        ],
        "user_registrations": [
            {"date": datetime.now().date(), "count": 12},
            {"date": (datetime.now() - timedelta(days=1)).date(), "count": 8},
            {"date": (datetime.now() - timedelta(days=2)).date(), "count": 15}
        ],
        "property_views": [
            {"property_id": 1, "views": 25, "date": datetime.now().date()},
            {"property_id": 2, "views": 18, "date": datetime.now().date()},
            {"property_id": 3, "views": 32, "date": datetime.now().date()}
        ],
        "search_queries": [
            {"query": "квартира", "count": 45},
            {"query": "дом", "count": 23},
            {"query": "аренда", "count": 67}
        ]
    } 