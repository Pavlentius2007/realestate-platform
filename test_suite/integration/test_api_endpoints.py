"""
Интеграционные тесты для API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_health_check(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


class TestAuthEndpoints:
    """Тесты для endpoints аутентификации"""
    
    def test_register_user(self, client: TestClient, test_db: Session):
        """Тест регистрации пользователя"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User",
            "phone": "+1234567890"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "id" in data
        assert "password" not in data  # Пароль не должен возвращаться
    
    def test_login_user(self, client: TestClient, test_db: Session, test_user_data):
        """Тест входа пользователя"""
        # Сначала регистрируем пользователя
        register_response = client.post("/api/auth/register", json=test_user_data)
        assert register_response.status_code == 201
        
        # Теперь логинимся
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        
        response = client.post("/api/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client: TestClient, test_db: Session):
        """Тест входа с неверными данными"""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/auth/login", data=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def test_get_current_user(self, authenticated_client: TestClient):
        """Тест получения текущего пользователя"""
        response = authenticated_client.get("/api/auth/me")
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "username" in data
        assert "email" in data
        assert "password" not in data


class TestPropertiesEndpoints:
    """Тесты для endpoints недвижимости"""
    
    def test_get_properties_list(self, client: TestClient, test_db: Session, sample_properties):
        """Тест получения списка объектов недвижимости"""
        # Создаем тестовые объекты недвижимости
        for property_data in sample_properties:
            response = client.post("/api/properties/", json=property_data)
            assert response.status_code == 201
        
        # Получаем список
        response = client.get("/api/properties/")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["items"]) == len(sample_properties)
    
    def test_get_property_detail(self, client: TestClient, test_db: Session, sample_properties):
        """Тест получения деталей объекта недвижимости"""
        # Создаем объект недвижимости
        property_data = sample_properties[0]
        create_response = client.post("/api/properties/", json=property_data)
        assert create_response.status_code == 201
        property_id = create_response.json()["id"]
        
        # Получаем детали
        response = client.get(f"/api/properties/{property_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == property_id
        assert data["title"] == property_data["title"]
        assert data["price"] == property_data["price"]
    
    def test_create_property(self, authenticated_client: TestClient, test_property_data):
        """Тест создания объекта недвижимости"""
        response = authenticated_client.post("/api/properties/", json=test_property_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == test_property_data["title"]
        assert data["price"] == test_property_data["price"]
        assert data["property_type"] == test_property_data["property_type"]
        assert "id" in data
        assert "created_at" in data
    
    def test_update_property(self, authenticated_client: TestClient, test_db: Session, test_property_data):
        """Тест обновления объекта недвижимости"""
        # Создаем объект недвижимости
        create_response = authenticated_client.post("/api/properties/", json=test_property_data)
        assert create_response.status_code == 201
        property_id = create_response.json()["id"]
        
        # Обновляем
        update_data = {"title": "Updated Property Title", "price": 200000}
        response = authenticated_client.put(f"/api/properties/{property_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["price"] == update_data["price"]
    
    def test_delete_property(self, authenticated_client: TestClient, test_db: Session, test_property_data):
        """Тест удаления объекта недвижимости"""
        # Создаем объект недвижимости
        create_response = authenticated_client.post("/api/properties/", json=test_property_data)
        assert create_response.status_code == 201
        property_id = create_response.json()["id"]
        
        # Удаляем
        response = authenticated_client.delete(f"/api/properties/{property_id}")
        
        assert response.status_code == 204
        
        # Проверяем, что объект удален
        get_response = authenticated_client.get(f"/api/properties/{property_id}")
        assert get_response.status_code == 404
    
    def test_search_properties(self, client: TestClient, test_db: Session, sample_properties):
        """Тест поиска объектов недвижимости"""
        # Создаем тестовые объекты
        for property_data in sample_properties:
            response = client.post("/api/properties/", json=property_data)
            assert response.status_code == 201
        
        # Ищем по типу
        response = client.get("/api/properties/search?property_type=apartment")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) > 0
        
        # Проверяем, что все найденные объекты - квартиры
        for item in data["items"]:
            assert item["property_type"] == "apartment"


class TestProjectsEndpoints:
    """Тесты для endpoints проектов"""
    
    def test_get_projects_list(self, client: TestClient, test_db: Session, sample_projects):
        """Тест получения списка проектов"""
        # Создаем тестовые проекты
        for project_data in sample_projects:
            response = client.post("/api/projects/", json=project_data)
            assert response.status_code == 201
        
        # Получаем список
        response = client.get("/api/projects/")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) == len(sample_projects)
    
    def test_get_project_detail(self, client: TestClient, test_db: Session, sample_projects):
        """Тест получения деталей проекта"""
        # Создаем проект
        project_data = sample_projects[0]
        create_response = client.post("/api/projects/", json=project_data)
        assert create_response.status_code == 201
        project_id = create_response.json()["id"]
        
        # Получаем детали
        response = client.get(f"/api/projects/{project_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project_id
        assert data["name"] == project_data["name"]
        assert data["developer"] == project_data["developer"]


class TestArticlesEndpoints:
    """Тесты для endpoints статей"""
    
    def test_get_articles_list(self, client: TestClient, test_db: Session, sample_articles):
        """Тест получения списка статей"""
        # Создаем тестовые статьи
        for article_data in sample_articles:
            response = client.post("/api/articles/", json=article_data)
            assert response.status_code == 201
        
        # Получаем список
        response = client.get("/api/articles/")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) == len(sample_articles)
    
    def test_get_article_detail(self, client: TestClient, test_db: Session, sample_articles):
        """Тест получения деталей статьи"""
        # Создаем статью
        article_data = sample_articles[0]
        create_response = client.post("/api/articles/", json=article_data)
        assert create_response.status_code == 201
        article_id = create_response.json()["id"]
        
        # Получаем детали
        response = client.get(f"/api/articles/{article_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == article_id
        assert data["title"] == article_data["title"]
        assert data["content"] == article_data["content"]


class TestFavoritesEndpoints:
    """Тесты для endpoints избранного"""
    
    def test_add_to_favorites(self, authenticated_client: TestClient, test_db: Session, test_property_data):
        """Тест добавления в избранное"""
        # Создаем объект недвижимости
        property_response = authenticated_client.post("/api/properties/", json=test_property_data)
        assert property_response.status_code == 201
        property_id = property_response.json()["id"]
        
        # Добавляем в избранное
        response = authenticated_client.post(f"/api/favorites/{property_id}")
        
        assert response.status_code == 201
        data = response.json()
        assert data["property_id"] == property_id
    
    def test_get_favorites(self, authenticated_client: TestClient, test_db: Session, sample_properties):
        """Тест получения избранного"""
        # Создаем объекты недвижимости и добавляем в избранное
        for property_data in sample_properties[:2]:  # Добавляем первые 2
            property_response = authenticated_client.post("/api/properties/", json=property_data)
            assert property_response.status_code == 201
            property_id = property_response.json()["id"]
            
            favorite_response = authenticated_client.post(f"/api/favorites/{property_id}")
            assert favorite_response.status_code == 201
        
        # Получаем избранное
        response = authenticated_client.get("/api/favorites/")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 2
    
    def test_remove_from_favorites(self, authenticated_client: TestClient, test_db: Session, test_property_data):
        """Тест удаления из избранного"""
        # Создаем объект недвижимости
        property_response = authenticated_client.post("/api/properties/", json=test_property_data)
        assert property_response.status_code == 201
        property_id = property_response.json()["id"]
        
        # Добавляем в избранное
        add_response = authenticated_client.post(f"/api/favorites/{property_id}")
        assert add_response.status_code == 201
        
        # Удаляем из избранного
        response = authenticated_client.delete(f"/api/favorites/{property_id}")
        
        assert response.status_code == 204
        
        # Проверяем, что объект удален из избранного
        favorites_response = authenticated_client.get("/api/favorites/")
        assert favorites_response.status_code == 200
        data = favorites_response.json()
        assert len(data["items"]) == 0


class TestRentalRequestsEndpoints:
    """Тесты для endpoints заявок на аренду"""
    
    def test_create_rental_request(self, client: TestClient, test_db: Session, test_property_data):
        """Тест создания заявки на аренду"""
        # Создаем объект недвижимости
        property_response = client.post("/api/properties/", json=test_property_data)
        assert property_response.status_code == 201
        property_id = property_response.json()["id"]
        
        # Создаем заявку на аренду
        rental_request_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "property_id": property_id,
            "message": "Test rental request",
            "check_in_date": "2024-01-01",
            "check_out_date": "2024-01-31",
            "guests": 2
        }
        
        response = client.post("/api/rental-requests/", json=rental_request_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == rental_request_data["name"]
        assert data["email"] == rental_request_data["email"]
        assert data["property_id"] == property_id
        assert data["status"] == "pending"


class TestAIEndpoints:
    """Тесты для AI endpoints"""
    
    def test_ai_search(self, client: TestClient, mock_external_services):
        """Тест AI поиска"""
        search_data = {
            "query": "квартира в центре",
            "budget": 200000,
            "area_from": 50,
            "area_to": 100,
            "district": "Центральный"
        }
        
        response = client.post("/api/ai/search", json=search_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "suggestions" in data
    
    def test_ai_chat(self, client: TestClient, mock_external_services):
        """Тест AI чата"""
        chat_data = {
            "message": "Помогите найти квартиру",
            "session_id": "test_session"
        }
        
        response = client.post("/api/ai/chat", json=chat_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "session_id" in data


class TestAdminEndpoints:
    """Тесты для admin endpoints"""
    
    def test_admin_dashboard(self, admin_client: TestClient):
        """Тест админ панели"""
        response = admin_client.get("/api/admin/dashboard")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_properties" in data
        assert "total_users" in data
        assert "total_requests" in data
    
    def test_admin_users_list(self, admin_client: TestClient):
        """Тест списка пользователей в админке"""
        response = admin_client.get("/api/admin/users")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
    
    def test_admin_properties_list(self, admin_client: TestClient):
        """Тест списка недвижимости в админке"""
        response = admin_client.get("/api/admin/properties")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
    
    def test_admin_analytics(self, admin_client: TestClient):
        """Тест аналитики в админке"""
        response = admin_client.get("/api/admin/analytics")
        
        assert response.status_code == 200
        data = response.json()
        assert "page_views" in data
        assert "user_registrations" in data
        assert "property_views" in data


class TestErrorHandling:
    """Тесты обработки ошибок"""
    
    def test_404_not_found(self, client: TestClient):
        """Тест 404 ошибки"""
        response = client.get("/api/nonexistent-endpoint")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_422_validation_error(self, client: TestClient):
        """Тест ошибки валидации"""
        invalid_data = {
            "title": "",  # Пустой заголовок
            "price": -1000,  # Отрицательная цена
            "email": "invalid-email"  # Неверный email
        }
        
        response = client.post("/api/properties/", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_500_internal_error(self, client: TestClient, test_db: Session):
        """Тест внутренней ошибки сервера"""
        # Попытка создать объект с несуществующими данными
        invalid_data = {
            "title": "Test",
            "price": 100000,
            "property_type": "nonexistent_type"  # Несуществующий тип
        }
        
        response = client.post("/api/properties/", json=invalid_data)
        
        # Может быть 422 (валидация) или 500 (внутренняя ошибка)
        assert response.status_code in [422, 500]


class TestPagination:
    """Тесты пагинации"""
    
    def test_properties_pagination(self, client: TestClient, test_db: Session, sample_properties):
        """Тест пагинации для объектов недвижимости"""
        # Создаем много объектов недвижимости
        for i in range(25):
            property_data = sample_properties[0].copy()
            property_data["title"] = f"Property {i}"
            response = client.post("/api/properties/", json=property_data)
            assert response.status_code == 201
        
        # Первая страница
        response = client.get("/api/properties/?page=1&size=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["page"] == 1
        assert data["size"] == 10
        assert data["total"] == 25
        
        # Вторая страница
        response = client.get("/api/properties/?page=2&size=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["page"] == 2
        
        # Последняя страница
        response = client.get("/api/properties/?page=3&size=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5  # Осталось 5 объектов
        assert data["page"] == 3


class TestFiltering:
    """Тесты фильтрации"""
    
    def test_properties_filtering(self, client: TestClient, test_db: Session, sample_properties):
        """Тест фильтрации объектов недвижимости"""
        # Создаем объекты недвижимости
        for property_data in sample_properties:
            response = client.post("/api/properties/", json=property_data)
            assert response.status_code == 201
        
        # Фильтр по типу
        response = client.get("/api/properties/?property_type=apartment")
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["property_type"] == "apartment"
        
        # Фильтр по цене
        response = client.get("/api/properties/?price_min=100000&price_max=200000")
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert 100000 <= item["price"] <= 200000
        
        # Фильтр по району
        response = client.get("/api/properties/?district=Центральный")
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["district"] == "Центральный" 