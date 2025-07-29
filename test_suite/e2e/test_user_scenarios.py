"""
E2E тесты для пользовательских сценариев
"""

import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class TestUserScenarios:
    """E2E тесты пользовательских сценариев"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Настройка веб-драйвера"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Запуск в фоновом режиме
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        yield driver
        
        driver.quit()
    
    @pytest.fixture
    def base_url(self):
        """Базовый URL для тестов"""
        return "http://localhost:8002"
    
    def test_homepage_loading(self, driver, base_url):
        """Тест загрузки главной страницы"""
        driver.get(f"{base_url}/ru")
        
        # Проверяем основные элементы
        assert "Sianoro" in driver.title
        
        # Проверяем наличие основных секций
        hero_section = driver.find_element(By.CLASS_NAME, "hero-section")
        assert hero_section.is_displayed()
        
        # Проверяем навигацию
        navbar = driver.find_element(By.TAG_NAME, "nav")
        assert navbar.is_displayed()
        
        # Проверяем футер
        footer = driver.find_element(By.TAG_NAME, "footer")
        assert footer.is_displayed()
    
    def test_property_search(self, driver, base_url):
        """Тест поиска недвижимости"""
        driver.get(f"{base_url}/ru/properties")
        
        # Ждем загрузки страницы
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "property-filters"))
        )
        
        # Заполняем фильтры
        property_type_select = driver.find_element(By.NAME, "property_type")
        property_type_select.click()
        apartment_option = driver.find_element(By.XPATH, "//option[@value='apartment']")
        apartment_option.click()
        
        price_min_input = driver.find_element(By.NAME, "price_min")
        price_min_input.clear()
        price_min_input.send_keys("100000")
        
        price_max_input = driver.find_element(By.NAME, "price_max")
        price_max_input.clear()
        price_max_input.send_keys("300000")
        
        # Нажимаем кнопку поиска
        search_button = driver.find_element(By.CLASS_NAME, "search-button")
        search_button.click()
        
        # Ждем результатов
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "property-card"))
        )
        
        # Проверяем результаты
        property_cards = driver.find_elements(By.CLASS_NAME, "property-card")
        assert len(property_cards) > 0
    
    def test_property_detail_view(self, driver, base_url):
        """Тест просмотра деталей объекта недвижимости"""
        # Сначала переходим на страницу списка
        driver.get(f"{base_url}/ru/properties")
        
        # Ждем загрузки карточек
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "property-card"))
        )
        
        # Кликаем на первую карточку
        first_property = driver.find_element(By.CLASS_NAME, "property-card")
        first_property.click()
        
        # Ждем загрузки страницы деталей
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "property-detail"))
        )
        
        # Проверяем элементы страницы деталей
        property_title = driver.find_element(By.CLASS_NAME, "property-title")
        assert property_title.is_displayed()
        
        property_price = driver.find_element(By.CLASS_NAME, "property-price")
        assert property_price.is_displayed()
        
        property_description = driver.find_element(By.CLASS_NAME, "property-description")
        assert property_description.is_displayed()
        
        # Проверяем кнопки действий
        contact_button = driver.find_element(By.CLASS_NAME, "contact-button")
        assert contact_button.is_displayed()
        
        favorite_button = driver.find_element(By.CLASS_NAME, "favorite-button")
        assert favorite_button.is_displayed()
    
    def test_user_registration(self, driver, base_url):
        """Тест регистрации пользователя"""
        driver.get(f"{base_url}/ru/register")
        
        # Ждем загрузки формы
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "registration-form"))
        )
        
        # Заполняем форму
        username_input = driver.find_element(By.NAME, "username")
        username_input.send_keys(f"testuser_{int(time.time())}")
        
        email_input = driver.find_element(By.NAME, "email")
        email_input.send_keys(f"test_{int(time.time())}@example.com")
        
        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys("testpassword123")
        
        confirm_password_input = driver.find_element(By.NAME, "confirm_password")
        confirm_password_input.send_keys("testpassword123")
        
        full_name_input = driver.find_element(By.NAME, "full_name")
        full_name_input.send_keys("Test User")
        
        phone_input = driver.find_element(By.NAME, "phone")
        phone_input.send_keys("+1234567890")
        
        # Отправляем форму
        submit_button = driver.find_element(By.TYPE, "submit")
        submit_button.click()
        
        # Ждем успешной регистрации
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        
        # Проверяем сообщение об успехе
        success_message = driver.find_element(By.CLASS_NAME, "success-message")
        assert "успешно" in success_message.text.lower()
    
    def test_user_login(self, driver, base_url):
        """Тест входа пользователя"""
        driver.get(f"{base_url}/ru/login")
        
        # Ждем загрузки формы
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "login-form"))
        )
        
        # Заполняем форму
        username_input = driver.find_element(By.NAME, "username")
        username_input.send_keys("testuser")
        
        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys("testpassword123")
        
        # Отправляем форму
        submit_button = driver.find_element(By.TYPE, "submit")
        submit_button.click()
        
        # Ждем успешного входа
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "user-menu"))
        )
        
        # Проверяем, что пользователь залогинен
        user_menu = driver.find_element(By.CLASS_NAME, "user-menu")
        assert user_menu.is_displayed()
    
    def test_add_to_favorites(self, driver, base_url):
        """Тест добавления в избранное"""
        # Сначала логинимся
        self.test_user_login(driver, base_url)
        
        # Переходим на страницу объекта недвижимости
        driver.get(f"{base_url}/ru/properties")
        
        # Ждем загрузки карточек
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "property-card"))
        )
        
        # Кликаем на кнопку избранного
        favorite_button = driver.find_element(By.CLASS_NAME, "favorite-button")
        favorite_button.click()
        
        # Ждем обновления состояния кнопки
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "favorite-button.active"))
        )
        
        # Проверяем, что объект добавлен в избранное
        active_favorite = driver.find_element(By.CLASS_NAME, "favorite-button.active")
        assert active_favorite.is_displayed()
    
    def test_contact_form(self, driver, base_url):
        """Тест формы обратной связи"""
        driver.get(f"{base_url}/ru/contacts")
        
        # Ждем загрузки формы
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "contact-form"))
        )
        
        # Заполняем форму
        name_input = driver.find_element(By.NAME, "name")
        name_input.send_keys("Test User")
        
        email_input = driver.find_element(By.NAME, "email")
        email_input.send_keys("test@example.com")
        
        phone_input = driver.find_element(By.NAME, "phone")
        phone_input.send_keys("+1234567890")
        
        message_input = driver.find_element(By.NAME, "message")
        message_input.send_keys("Test message for contact form")
        
        # Отправляем форму
        submit_button = driver.find_element(By.TYPE, "submit")
        submit_button.click()
        
        # Ждем успешной отправки
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        
        # Проверяем сообщение об успехе
        success_message = driver.find_element(By.CLASS_NAME, "success-message")
        assert "отправлено" in success_message.text.lower()
    
    def test_rental_request(self, driver, base_url):
        """Тест заявки на аренду"""
        # Переходим на страницу объекта недвижимости
        driver.get(f"{base_url}/ru/properties")
        
        # Ждем загрузки карточек
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "property-card"))
        )
        
        # Кликаем на карточку
        first_property = driver.find_element(By.CLASS_NAME, "property-card")
        first_property.click()
        
        # Ждем загрузки страницы деталей
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "property-detail"))
        )
        
        # Кликаем на кнопку "Забронировать"
        rent_button = driver.find_element(By.CLASS_NAME, "rent-button")
        rent_button.click()
        
        # Ждем загрузки формы аренды
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "rental-form"))
        )
        
        # Заполняем форму
        name_input = driver.find_element(By.NAME, "name")
        name_input.send_keys("Test User")
        
        email_input = driver.find_element(By.NAME, "email")
        email_input.send_keys("test@example.com")
        
        phone_input = driver.find_element(By.NAME, "phone")
        phone_input.send_keys("+1234567890")
        
        check_in_input = driver.find_element(By.NAME, "check_in_date")
        check_in_input.send_keys("2024-01-01")
        
        check_out_input = driver.find_element(By.NAME, "check_out_date")
        check_out_input.send_keys("2024-01-31")
        
        guests_input = driver.find_element(By.NAME, "guests")
        guests_input.send_keys("2")
        
        message_input = driver.find_element(By.NAME, "message")
        message_input.send_keys("Test rental request")
        
        # Отправляем форму
        submit_button = driver.find_element(By.TYPE, "submit")
        submit_button.click()
        
        # Ждем успешной отправки
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        
        # Проверяем сообщение об успехе
        success_message = driver.find_element(By.CLASS_NAME, "success-message")
        assert "отправлена" in success_message.text.lower()
    
    def test_ai_search(self, driver, base_url):
        """Тест AI поиска"""
        driver.get(f"{base_url}/ru/ai-search")
        
        # Ждем загрузки формы
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ai-search-form"))
        )
        
        # Заполняем форму AI поиска
        query_input = driver.find_element(By.NAME, "query")
        query_input.send_keys("квартира в центре с 2 спальнями")
        
        budget_input = driver.find_element(By.NAME, "budget")
        budget_input.send_keys("200000")
        
        area_from_input = driver.find_element(By.NAME, "area_from")
        area_from_input.send_keys("50")
        
        area_to_input = driver.find_element(By.NAME, "area_to")
        area_to_input.send_keys("100")
        
        # Отправляем форму
        submit_button = driver.find_element(By.TYPE, "submit")
        submit_button.click()
        
        # Ждем результатов
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ai-results"))
        )
        
        # Проверяем результаты
        results_section = driver.find_element(By.CLASS_NAME, "ai-results")
        assert results_section.is_displayed()
    
    def test_ai_chat(self, driver, base_url):
        """Тест AI чата"""
        driver.get(f"{base_url}/ru/ai-chat")
        
        # Ждем загрузки чата
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "chat-container"))
        )
        
        # Находим поле ввода сообщения
        message_input = driver.find_element(By.ID, "message-input")
        message_input.send_keys("Помогите найти квартиру в центре")
        
        # Отправляем сообщение
        send_button = driver.find_element(By.ID, "send-button")
        send_button.click()
        
        # Ждем ответа AI
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ai-message"))
        )
        
        # Проверяем ответ
        ai_message = driver.find_element(By.CLASS_NAME, "ai-message")
        assert ai_message.is_displayed()
        assert len(ai_message.text) > 0
    
    def test_language_switching(self, driver, base_url):
        """Тест переключения языков"""
        driver.get(f"{base_url}/ru")
        
        # Проверяем, что страница на русском
        page_title = driver.title
        assert "рус" in page_title.lower() or "ru" in page_title.lower()
        
        # Переключаемся на английский
        language_switcher = driver.find_element(By.CLASS_NAME, "language-switcher")
        english_option = language_switcher.find_element(By.XPATH, "//a[@href='/en']")
        english_option.click()
        
        # Ждем загрузки страницы на английском
        WebDriverWait(driver, 10).until(
            EC.url_contains("/en")
        )
        
        # Проверяем, что страница на английском
        new_page_title = driver.title
        assert "en" in driver.current_url.lower()
        
        # Переключаемся обратно на русский
        language_switcher = driver.find_element(By.CLASS_NAME, "language-switcher")
        russian_option = language_switcher.find_element(By.XPATH, "//a[@href='/ru']")
        russian_option.click()
        
        # Ждем загрузки страницы на русском
        WebDriverWait(driver, 10).until(
            EC.url_contains("/ru")
        )
        
        # Проверяем, что страница на русском
        assert "ru" in driver.current_url.lower()
    
    def test_mobile_responsiveness(self, driver, base_url):
        """Тест адаптивности для мобильных устройств"""
        # Устанавливаем размер окна для мобильного устройства
        driver.set_window_size(375, 667)  # iPhone размер
        
        driver.get(f"{base_url}/ru")
        
        # Проверяем, что мобильное меню доступно
        mobile_menu_button = driver.find_element(By.CLASS_NAME, "mobile-menu-toggle")
        assert mobile_menu_button.is_displayed()
        
        # Открываем мобильное меню
        mobile_menu_button.click()
        
        # Ждем открытия меню
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "mobile-menu.active"))
        )
        
        # Проверяем элементы мобильного меню
        mobile_menu = driver.find_element(By.CLASS_NAME, "mobile-menu.active")
        assert mobile_menu.is_displayed()
        
        # Закрываем меню
        close_button = driver.find_element(By.CLASS_NAME, "mobile-menu-close")
        close_button.click()
        
        # Ждем закрытия меню
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "mobile-menu.active"))
        )
        
        # Возвращаем нормальный размер окна
        driver.set_window_size(1920, 1080)
    
    def test_performance_metrics(self, driver, base_url):
        """Тест метрик производительности"""
        # Включаем сбор метрик
        driver.execute_script("window.performance.mark('test-start')")
        
        driver.get(f"{base_url}/ru")
        
        # Ждем полной загрузки страницы
        WebDriverWait(driver, 10).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        
        # Отмечаем конец теста
        driver.execute_script("window.performance.mark('test-end')")
        driver.execute_script("window.performance.measure('page-load', 'test-start', 'test-end')")
        
        # Получаем метрики
        navigation_timing = driver.execute_script("""
            var perfData = window.performance.getEntriesByType('navigation')[0];
            return {
                domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
                loadComplete: perfData.loadEventEnd - perfData.loadEventStart,
                totalLoadTime: perfData.loadEventEnd - perfData.fetchStart
            };
        """)
        
        # Проверяем, что время загрузки приемлемое
        assert navigation_timing["domContentLoaded"] < 3000  # менее 3 секунд
        assert navigation_timing["totalLoadTime"] < 5000  # менее 5 секунд
    
    def test_accessibility(self, driver, base_url):
        """Тест доступности"""
        driver.get(f"{base_url}/ru")
        
        # Проверяем наличие alt атрибутов у изображений
        images = driver.find_elements(By.TAG_NAME, "img")
        for img in images:
            alt = img.get_attribute("alt")
            assert alt is not None and alt != "", "Изображение должно иметь alt атрибут"
        
        # Проверяем наличие заголовков
        headings = driver.find_elements(By.XPATH, "//h1 | //h2 | //h3 | //h4 | //h5 | //h6")
        assert len(headings) > 0, "Страница должна содержать заголовки"
        
        # Проверяем контрастность (базовая проверка)
        body = driver.find_element(By.TAG_NAME, "body")
        background_color = body.value_of_css_property("background-color")
        color = body.value_of_css_property("color")
        
        # Простая проверка, что цвета не одинаковые
        assert background_color != color, "Цвет текста должен отличаться от цвета фона"
    
    def test_error_pages(self, driver, base_url):
        """Тест страниц ошибок"""
        # Тестируем 404 страницу
        driver.get(f"{base_url}/nonexistent-page")
        
        # Ждем загрузки страницы ошибки
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "error-page"))
        )
        
        # Проверяем элементы страницы ошибки
        error_title = driver.find_element(By.CLASS_NAME, "error-title")
        assert "404" in error_title.text or "не найдено" in error_title.text.lower()
        
        # Проверяем кнопку возврата на главную
        home_button = driver.find_element(By.CLASS_NAME, "home-button")
        assert home_button.is_displayed()
        
        # Кликаем на кнопку возврата
        home_button.click()
        
        # Проверяем, что вернулись на главную
        WebDriverWait(driver, 10).until(
            EC.url_contains("/ru")
        ) 