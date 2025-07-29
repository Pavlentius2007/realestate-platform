"""
Performance тесты для нагрузочного тестирования
"""

import pytest
import time
import requests
import threading
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from fastapi.testclient import TestClient


class TestPerformance:
    """Performance тесты"""
    
    def test_homepage_load_time(self, client: TestClient):
        """Тест времени загрузки главной страницы"""
        start_time = time.time()
        
        response = client.get("/ru")
        
        end_time = time.time()
        load_time = end_time - start_time
        
        assert response.status_code == 200
        assert load_time < 2.0  # Менее 2 секунд
        
        print(f"Главная страница загружена за {load_time:.2f} секунд")
    
    def test_properties_list_load_time(self, client: TestClient):
        """Тест времени загрузки списка недвижимости"""
        start_time = time.time()
        
        response = client.get("/ru/properties")
        
        end_time = time.time()
        load_time = end_time - start_time
        
        assert response.status_code == 200
        assert load_time < 3.0  # Менее 3 секунд
        
        print(f"Список недвижимости загружен за {load_time:.2f} секунд")
    
    def test_property_detail_load_time(self, client: TestClient, test_db: Session, test_property_data):
        """Тест времени загрузки деталей объекта недвижимости"""
        # Создаем объект недвижимости
        create_response = client.post("/api/properties/", json=test_property_data)
        assert create_response.status_code == 201
        property_id = create_response.json()["id"]
        
        start_time = time.time()
        
        response = client.get(f"/ru/properties/{property_id}")
        
        end_time = time.time()
        load_time = end_time - start_time
        
        assert response.status_code == 200
        assert load_time < 2.0  # Менее 2 секунд
        
        print(f"Детали объекта загружены за {load_time:.2f} секунд")
    
    def test_search_performance(self, client: TestClient, test_db: Session, sample_properties):
        """Тест производительности поиска"""
        # Создаем тестовые объекты
        for property_data in sample_properties:
            response = client.post("/api/properties/", json=property_data)
            assert response.status_code == 201
        
        search_queries = [
            "квартира",
            "дом",
            "студия",
            "центр",
            "новостройка"
        ]
        
        search_times = []
        
        for query in search_queries:
            start_time = time.time()
            
            response = client.get(f"/ru/search?q={query}")
            
            end_time = time.time()
            search_time = end_time - start_time
            search_times.append(search_time)
            
            assert response.status_code == 200
            assert search_time < 2.0  # Менее 2 секунд
        
        avg_search_time = statistics.mean(search_times)
        max_search_time = max(search_times)
        
        print(f"Среднее время поиска: {avg_search_time:.2f} секунд")
        print(f"Максимальное время поиска: {max_search_time:.2f} секунд")
        
        assert avg_search_time < 1.5  # Среднее время менее 1.5 секунд
        assert max_search_time < 2.0  # Максимальное время менее 2 секунд
    
    def test_concurrent_requests(self, client: TestClient):
        """Тест одновременных запросов"""
        def make_request():
            start_time = time.time()
            response = client.get("/ru")
            end_time = time.time()
            return {
                "status_code": response.status_code,
                "response_time": end_time - start_time
            }
        
        # Выполняем 10 одновременных запросов
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in as_completed(futures)]
        
        # Проверяем результаты
        for result in results:
            assert result["status_code"] == 200
            assert result["response_time"] < 3.0  # Менее 3 секунд
        
        response_times = [r["response_time"] for r in results]
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        print(f"Среднее время ответа при 10 одновременных запросах: {avg_response_time:.2f} секунд")
        print(f"Максимальное время ответа: {max_response_time:.2f} секунд")
        
        assert avg_response_time < 2.0  # Среднее время менее 2 секунд
        assert max_response_time < 3.0  # Максимальное время менее 3 секунд
    
    def test_database_query_performance(self, client: TestClient, test_db: Session, sample_properties):
        """Тест производительности запросов к базе данных"""
        # Создаем много объектов недвижимости
        for i in range(50):
            property_data = sample_properties[0].copy()
            property_data["title"] = f"Property {i}"
            property_data["price"] = 100000 + (i * 10000)
            
            response = client.post("/api/properties/", json=property_data)
            assert response.status_code == 201
        
        # Тестируем различные запросы
        queries = [
            "/api/properties/",
            "/api/properties/?page=1&size=10",
            "/api/properties/?property_type=apartment",
            "/api/properties/?price_min=100000&price_max=200000",
            "/api/properties/?district=Центральный"
        ]
        
        query_times = []
        
        for query in queries:
            start_time = time.time()
            
            response = client.get(query)
            
            end_time = time.time()
            query_time = end_time - start_time
            query_times.append(query_time)
            
            assert response.status_code == 200
            assert query_time < 2.0  # Менее 2 секунд
        
        avg_query_time = statistics.mean(query_times)
        max_query_time = max(query_times)
        
        print(f"Среднее время запроса к БД: {avg_query_time:.2f} секунд")
        print(f"Максимальное время запроса: {max_query_time:.2f} секунд")
        
        assert avg_query_time < 1.0  # Среднее время менее 1 секунды
        assert max_query_time < 2.0  # Максимальное время менее 2 секунд
    
    def test_memory_usage(self, client: TestClient):
        """Тест использования памяти"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Выполняем множество запросов
        for i in range(100):
            response = client.get("/ru")
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"Начальное использование памяти: {initial_memory:.2f} MB")
        print(f"Конечное использование памяти: {final_memory:.2f} MB")
        print(f"Увеличение памяти: {memory_increase:.2f} MB")
        
        # Проверяем, что утечки памяти нет
        assert memory_increase < 50  # Увеличение менее 50 MB
    
    def test_file_upload_performance(self, client: TestClient, temp_image_file):
        """Тест производительности загрузки файлов"""
        # Читаем тестовый файл
        with open(temp_image_file, 'rb') as f:
            file_content = f.read()
        
        start_time = time.time()
        
        files = {
            'file': ('test_image.jpg', file_content, 'image/jpeg')
        }
        
        response = client.post("/api/upload", files=files)
        
        end_time = time.time()
        upload_time = end_time - start_time
        
        assert response.status_code in [200, 201]
        assert upload_time < 5.0  # Менее 5 секунд
        
        print(f"Файл загружен за {upload_time:.2f} секунд")
    
    def test_api_response_size(self, client: TestClient, test_db: Session, sample_properties):
        """Тест размера ответов API"""
        # Создаем тестовые объекты
        for property_data in sample_properties:
            response = client.post("/api/properties/", json=property_data)
            assert response.status_code == 201
        
        # Тестируем различные endpoints
        endpoints = [
            "/api/properties/",
            "/api/projects/",
            "/api/articles/"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            
            response_size = len(response.content)
            response_size_mb = response_size / 1024 / 1024
            
            print(f"Размер ответа {endpoint}: {response_size_mb:.2f} MB")
            
            # Проверяем, что размер ответа разумный
            assert response_size_mb < 1.0  # Менее 1 MB
    
    def test_caching_performance(self, client: TestClient):
        """Тест производительности кэширования"""
        # Первый запрос (без кэша)
        start_time = time.time()
        response1 = client.get("/ru")
        first_request_time = time.time() - start_time
        
        # Второй запрос (с кэшем)
        start_time = time.time()
        response2 = client.get("/ru")
        second_request_time = time.time() - start_time
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Второй запрос должен быть быстрее
        assert second_request_time <= first_request_time
        
        print(f"Первый запрос: {first_request_time:.2f} секунд")
        print(f"Второй запрос: {second_request_time:.2f} секунд")
        print(f"Ускорение: {first_request_time / second_request_time:.2f}x")
    
    def test_stress_test(self, client: TestClient):
        """Стресс-тест"""
        def stress_request():
            try:
                start_time = time.time()
                response = client.get("/ru")
                end_time = time.time()
                
                return {
                    "success": response.status_code == 200,
                    "response_time": end_time - start_time,
                    "status_code": response.status_code
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "response_time": None
                }
        
        # Выполняем 50 одновременных запросов
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(stress_request) for _ in range(50)]
            results = [future.result() for future in as_completed(futures)]
        
        # Анализируем результаты
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]
        
        success_rate = len(successful_requests) / len(results) * 100
        
        print(f"Успешных запросов: {len(successful_requests)}")
        print(f"Неудачных запросов: {len(failed_requests)}")
        print(f"Процент успеха: {success_rate:.1f}%")
        
        if successful_requests:
            response_times = [r["response_time"] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            
            print(f"Среднее время ответа: {avg_response_time:.2f} секунд")
            print(f"Максимальное время ответа: {max_response_time:.2f} секунд")
            
            assert avg_response_time < 3.0  # Среднее время менее 3 секунд
            assert max_response_time < 5.0  # Максимальное время менее 5 секунд
        
        # Проверяем, что большинство запросов успешны
        assert success_rate > 90  # Более 90% успешных запросов
    
    def test_database_connection_pool(self, client: TestClient, test_db: Session):
        """Тест пула соединений с базой данных"""
        def db_request():
            start_time = time.time()
            response = client.get("/api/properties/")
            end_time = time.time()
            return end_time - start_time
        
        # Выполняем множество запросов к БД
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(db_request) for _ in range(100)]
            response_times = [future.result() for future in as_completed(futures)]
        
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        print(f"Среднее время запроса к БД: {avg_response_time:.2f} секунд")
        print(f"Минимальное время: {min_response_time:.2f} секунд")
        print(f"Максимальное время: {max_response_time:.2f} секунд")
        
        # Проверяем стабильность
        assert avg_response_time < 1.0  # Среднее время менее 1 секунды
        assert max_response_time < 2.0  # Максимальное время менее 2 секунд
        assert max_response_time / min_response_time < 5  # Разброс не более 5x
    
    def test_session_management_performance(self, client: TestClient):
        """Тест производительности управления сессиями"""
        def session_request():
            # Создаем новую сессию
            session = requests.Session()
            
            start_time = time.time()
            
            # Выполняем несколько запросов в одной сессии
            response1 = session.get("http://localhost:8002/ru")
            response2 = session.get("http://localhost:8002/ru/properties")
            response3 = session.get("http://localhost:8002/ru/projects")
            
            end_time = time.time()
            
            session.close()
            
            return {
                "total_time": end_time - start_time,
                "requests_count": 3,
                "avg_time": (end_time - start_time) / 3
            }
        
        # Тестируем множество сессий
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(session_request) for _ in range(10)]
            results = [future.result() for future in as_completed(futures)]
        
        avg_session_time = statistics.mean([r["avg_time"] for r in results])
        max_session_time = max([r["avg_time"] for r in results])
        
        print(f"Среднее время запроса в сессии: {avg_session_time:.2f} секунд")
        print(f"Максимальное время запроса в сессии: {max_session_time:.2f} секунд")
        
        assert avg_session_time < 1.5  # Среднее время менее 1.5 секунд
        assert max_session_time < 3.0  # Максимальное время менее 3 секунд


class TestLoadTesting:
    """Нагрузочное тестирование"""
    
    def test_gradual_load_increase(self, client: TestClient):
        """Тест постепенного увеличения нагрузки"""
        def make_request():
            start_time = time.time()
            response = client.get("/ru")
            end_time = time.time()
            return {
                "status_code": response.status_code,
                "response_time": end_time - start_time
            }
        
        # Постепенно увеличиваем нагрузку
        load_levels = [1, 5, 10, 20, 30]
        results_by_level = {}
        
        for load_level in load_levels:
            print(f"Тестируем нагрузку: {load_level} одновременных запросов")
            
            with ThreadPoolExecutor(max_workers=load_level) as executor:
                futures = [executor.submit(make_request) for _ in range(load_level)]
                results = [future.result() for future in as_completed(futures)]
            
            successful_requests = [r for r in results if r["status_code"] == 200]
            response_times = [r["response_time"] for r in successful_requests]
            
            if response_times:
                avg_time = statistics.mean(response_times)
                max_time = max(response_times)
                success_rate = len(successful_requests) / len(results) * 100
                
                results_by_level[load_level] = {
                    "avg_time": avg_time,
                    "max_time": max_time,
                    "success_rate": success_rate
                }
                
                print(f"  Среднее время: {avg_time:.2f} сек")
                print(f"  Максимальное время: {max_time:.2f} сек")
                print(f"  Процент успеха: {success_rate:.1f}%")
                
                # Проверяем, что производительность не падает критически
                assert success_rate > 80  # Более 80% успешных запросов
                assert avg_time < 5.0  # Среднее время менее 5 секунд
        
        # Анализируем тренд
        print("\nАнализ тренда производительности:")
        for level, metrics in results_by_level.items():
            print(f"Нагрузка {level}: {metrics['avg_time']:.2f}с, {metrics['success_rate']:.1f}%")
    
    def test_sustained_load(self, client: TestClient):
        """Тест длительной нагрузки"""
        def sustained_request():
            for _ in range(10):  # 10 запросов подряд
                start_time = time.time()
                response = client.get("/ru")
                end_time = time.time()
                
                yield {
                    "status_code": response.status_code,
                    "response_time": end_time - start_time
                }
        
        # Выполняем длительную нагрузку
        all_results = []
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(lambda: list(sustained_request())) for _ in range(5)]
            
            for future in as_completed(futures):
                results = future.result()
                all_results.extend(results)
        
        # Анализируем результаты
        successful_requests = [r for r in all_results if r["status_code"] == 200]
        response_times = [r["response_time"] for r in successful_requests]
        
        if response_times:
            avg_time = statistics.mean(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            print(f"Длительная нагрузка (50 запросов):")
            print(f"  Среднее время: {avg_time:.2f} сек")
            print(f"  Минимальное время: {min_time:.2f} сек")
            print(f"  Максимальное время: {max_time:.2f} сек")
            print(f"  Процент успеха: {len(successful_requests) / len(all_results) * 100:.1f}%")
            
            # Проверяем стабильность
            assert avg_time < 2.0  # Среднее время менее 2 секунд
            assert max_time < 5.0  # Максимальное время менее 5 секунд
            assert len(successful_requests) / len(all_results) > 0.9  # Более 90% успеха 