"""
Конфигурация pytest для тестовой системы Sianoro
"""

import pytest
import asyncio
import tempfile
import os
import sys
from pathlib import Path
from typing import Generator, Dict, Any
from unittest.mock import Mock, patch

# Добавляем пути для импорта
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

# Импорты для тестирования
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import sessionmaker, Session, declarative_base, relationship
from sqlalchemy.pool import StaticPool
from datetime import datetime

# Импорты приложения - используем только один корректный путь
from backend.main import app
from backend.database import get_db
from backend.config.settings import settings

# Создаем тестовую базу для тестов
TestBase = declarative_base()

# Тестовые модели без PostgreSQL-специфичных типов
class TestUser(TestBase):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False, default="Пользователь")
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    source = Column(String, nullable=True)
    telegram_id = Column(String, nullable=True)
    whatsapp_number = Column(String, nullable=True)
    instagram_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    budget_min = Column(Integer, nullable=True)
    budget_max = Column(Integer, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    property_type = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    priority = Column(String, nullable=True, default="medium")
    status = Column(String, nullable=True, default="new")
    is_active = Column(Boolean, nullable=True, default=True)
    last_contact = Column(DateTime, nullable=True)
    def __repr__(self):
        return f"<User {self.email}>"

class TestProperty(TestBase):
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    condo_name = Column(String, nullable=True)
    property_type = Column("type", String, nullable=True)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    price_period = Column(String, nullable=True)
    location = Column(String, nullable=True)
    district = Column(String, nullable=True)
    area = Column(Float, nullable=True)
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Integer, nullable=True)
    floor = Column(String, nullable=True)
    furnished = Column(String, nullable=True)
    published_at = Column(String, nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    features = Column(Text, nullable=True)  # JSON строка вместо ARRAY
    status = Column(String, nullable=True)
    land_area = Column(Float, nullable=True)
    old_price = Column(Float, nullable=True)
    is_new_building = Column(Boolean, default=False, nullable=True)
    deal_type = Column(String, nullable=True)
    currency = Column(String, default="THB", nullable=True)
    short_description = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    whatsapp = Column(String, nullable=True)
    amenities = Column(String, nullable=True)
    rental_status = Column(String, default="available", nullable=True)
    rental_start_date = Column(DateTime, nullable=True)
    rental_end_date = Column(DateTime, nullable=True)
    renter_name = Column(String, nullable=True)
    renter_contact = Column(String, nullable=True)
    rental_notes = Column(String, nullable=True)
    def __repr__(self):
        return f"<Property {self.title}>"

class TestPropertyImage(TestBase):
    __tablename__ = "property_images"
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    image_url = Column(String, nullable=False)

class TestProject(TestBase):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    subtitle = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    district = Column(String, nullable=True)
    developer = Column(String, nullable=True)
    completion_year = Column(Integer, nullable=True)
    total_units = Column(Integer, nullable=True)
    floors = Column(Integer, nullable=True)
    price_from = Column(Float, nullable=True)
    price_to = Column(Float, nullable=True)
    currency = Column(String, default="THB", nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    hero_image = Column(String, nullable=True)
    gallery_images = Column(Text, nullable=True)  # JSON строка вместо ARRAY
    video_url = Column(String, nullable=True)
    highlights = Column(Text, nullable=True)  # JSON строка вместо ARRAY
    amenities = Column(Text, nullable=True)  # JSON строка вместо ARRAY
    unit_types = Column(Text, nullable=True)
    payment_plan = Column(Text, nullable=True)
    down_payment = Column(String, nullable=True)
    monthly_payment = Column(String, nullable=True)
    roi_info = Column(Text, nullable=True)
    sales_office_address = Column(String, nullable=True)
    sales_office_phone = Column(String, nullable=True)
    sales_office_email = Column(String, nullable=True)
    status = Column(String, default="active", nullable=True)
    is_featured = Column(Boolean, default=False)
    meta_title = Column(String, nullable=True)
    meta_description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    def __repr__(self):
        return f"<Project(slug='{self.slug}', title='{self.title}')>"

class TestFavorite(TestBase):
    __tablename__ = "favorites"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Добавляем ограничение уникальности
    __table_args__ = (
        UniqueConstraint('session_id', 'property_id', name='uq_favorite_session_property'),
    )

# Конфигурация pytest
def pytest_configure(config):
    """Конфигурация pytest"""
    config.addinivalue_line(
        "markers", "unit: Unit тесты"
    )
    config.addinivalue_line(
        "markers", "integration: Интеграционные тесты"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end тесты"
    )
    config.addinivalue_line(
        "markers", "security: Тесты безопасности"
    )
    config.addinivalue_line(
        "markers", "performance: Performance тесты"
    )
    config.addinivalue_line(
        "markers", "slow: Медленные тесты"
    )

# Фикстуры для базы данных
@pytest.fixture(scope="session")
def test_db_engine():
    """Создает тестовый движок базы данных"""
    # Создаем временную SQLite базу для тестов
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Создаем все таблицы
    TestBase.metadata.create_all(bind=engine)
    yield engine
    # Очистка
    engine.dispose()

@pytest.fixture(scope="function")
def test_db_session(test_db_engine) -> Generator[Session, None, None]:
    """Создает тестовую сессию базы данных"""
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=test_db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(scope="function")
def test_db(test_db_session):
    """Фикстура для переопределения зависимости get_db"""
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    yield test_db_session
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def client(test_db) -> Generator[TestClient, None, None]:
    """Создает тестовый клиент FastAPI"""
    with TestClient(app) as test_client:
        yield test_client

# Фикстуры для тестовых данных
@pytest.fixture(scope="function") 
def test_user_data() -> Dict[str, Any]:
    """Тестовые данные пользователя"""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "phone": "+1234567890"
    }

@pytest.fixture(scope="function")
def test_property_data() -> Dict[str, Any]:
    """Тестовые данные недвижимости"""
    return {
        "title": "Test Property",
        "description": "Test property description",
        "price": 100000,
        "currency": "USD",
        "property_type": "apartment",
        "bedrooms": 2,
        "bathrooms": 1,
        "area": 75.5,
        "floor": "5",
        "district": "Test District",
        "furnished": "Yes",
        "status": "active"
    }

@pytest.fixture(scope="function")
def test_admin_data() -> Dict[str, Any]:
    """Тестовые данные администратора"""
    return {
        "email": "admin@example.com",
        "password": "adminpassword123",
        "full_name": "Admin User",
        "phone": "+1234567890"
    }

# Фикстуры для аутентификации
@pytest.fixture(scope="function")
def authenticated_client(client, test_db, test_user_data):
    """Клиент с аутентифицированным пользователем"""
    from backend.utils.auth import AuthService
    hashed_password = AuthService.hash_password(test_user_data["password"])
    user = TestUser(
        email=test_user_data["email"],
        hashed_password=hashed_password,
        full_name=test_user_data["full_name"],
        phone=test_user_data["phone"]
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    login_response = client.post("/api/auth/login", data={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    if login_response.status_code == 200:
        token = login_response.json().get("access_token")
        client.headers.update({"Authorization": f"Bearer {token}"})
    return client

@pytest.fixture(scope="function")
def admin_client(client, test_db, test_admin_data):
    """Клиент с аутентифицированным администратором"""
    from backend.utils.auth import AuthService
    hashed_password = AuthService.hash_password(test_admin_data["password"])
    admin = TestUser(
        email=test_admin_data["email"],
        hashed_password=hashed_password,
        full_name=test_admin_data["full_name"],
        phone=test_admin_data["phone"]
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    login_response = client.post("/api/auth/login", data={
        "email": test_admin_data["email"],
        "password": test_admin_data["password"]
    })
    if login_response.status_code == 200:
        token = login_response.json().get("access_token")
        client.headers.update({"Authorization": f"Bearer {token}"})
    return client

# Фикстуры для временных файлов
@pytest.fixture(scope="function")
def temp_file():
    """Создает временный файл"""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"test content")
        temp_path = f.name
    yield temp_path
    if os.path.exists(temp_path):
        os.unlink(temp_path)

@pytest.fixture(scope="function")
def temp_image_file():
    """Создает временный файл изображения"""
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\x27 ,#\x1c\x1c(7),01444\x1f\x27=9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9")
        temp_path = f.name
    yield temp_path
    if os.path.exists(temp_path):
        os.unlink(temp_path)

# Фикстуры для моков
@pytest.fixture(scope="function")
def mock_external_services():
    """Мокает внешние сервисы"""
    with patch("backend.services.ai_assistant.openai.ChatCompletion.create") as mock_openai, \
         patch("backend.services.ai_assistant.requests.post") as mock_requests, \
         patch("backend.utils.auth.send_email") as mock_email:
        mock_openai.return_value = Mock(
            choices=[Mock(message=Mock(content="Test AI response"))]
        )
        mock_requests.return_value = Mock(
            status_code=200,
            json=lambda: {"translatedText": "Test translation"}
        )
        mock_email.return_value = True
        yield {
            "openai": mock_openai,
            "requests": mock_requests,
            "email": mock_email
        }

# Фикстуры для асинхронных тестов
@pytest.fixture(scope="session")
def event_loop():
    """Создает event loop для асинхронных тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Фикстуры для тестов производительности
@pytest.fixture(scope="function")
def performance_timer():
    """Таймер для performance тестов"""
    import time
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        def start(self):
            self.start_time = time.time()
        def stop(self):
            self.end_time = time.time()
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    return Timer()

# Фикстуры для тестов безопасности
@pytest.fixture(scope="function")
def security_test_data():
    """Данные для тестов безопасности"""
    return {
        "xss_payloads": [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
            "<svg onload=alert('XSS')>"
        ],
        "sql_injection_payloads": [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "' OR 1=1#"
        ],
        "path_traversal_payloads": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
    }

# Настройки для разных типов тестов
def pytest_collection_modifyitems(config, items):
    """Модифицирует коллекцию тестов"""
    for item in items:
        if "test_unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        elif "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "test_e2e" in item.nodeid:
            item.add_marker(pytest.mark.e2e)
        elif "test_security" in item.nodeid:
            item.add_marker(pytest.mark.security)
        elif "test_performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)
        if any(keyword in item.nodeid for keyword in ["performance", "e2e", "load"]):
            item.add_marker(pytest.mark.slow) 