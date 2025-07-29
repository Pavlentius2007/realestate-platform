# Тестовая система Sianoro

Комплексная система тестирования для проекта Sianoro, включающая все типы тестов: Unit, Integration, E2E, Security и Performance.

## 📁 Структура проекта

```
test_suite/
├── conftest.py                 # Конфигурация pytest и фикстуры
├── pytest.ini                 # Настройки pytest
├── run_tests.py               # Главный скрипт запуска тестов
├── README.md                  # Этот файл
├── unit/                      # Unit тесты
│   ├── test_models.py         # Тесты моделей
│   ├── test_services.py       # Тесты сервисов
│   └── test_utils.py          # Тесты утилит
├── integration/               # Интеграционные тесты
│   ├── test_api_endpoints.py  # Тесты API endpoints
│   ├── test_database.py       # Тесты базы данных
│   └── test_external_apis.py  # Тесты внешних API
├── e2e/                       # E2E тесты
│   ├── test_user_scenarios.py # Пользовательские сценарии
│   ├── test_admin_flows.py    # Админские сценарии
│   └── test_mobile.py         # Мобильные тесты
├── security/                  # Тесты безопасности
│   ├── test_security_vulnerabilities.py # Тесты уязвимостей
│   ├── test_authentication.py # Тесты аутентификации
│   └── test_authorization.py  # Тесты авторизации
├── performance/               # Performance тесты
│   ├── test_performance.py    # Нагрузочные тесты
│   ├── test_load_testing.py   # Стресс-тестирование
│   └── test_benchmarks.py     # Бенчмарки
├── fixtures/                  # Фикстуры
│   ├── __init__.py
│   ├── test_data.py          # Тестовые данные
│   ├── database_fixtures.py  # Фикстуры БД
│   └── auth_fixtures.py      # Фикстуры аутентификации
├── config/                    # Конфигурация
│   ├── test_config.py        # Конфигурация тестов
│   └── test_settings.py      # Настройки тестов
├── reports/                   # Отчеты
│   ├── coverage/             # Отчеты покрытия
│   ├── html/                 # HTML отчеты
│   └── junit/                # JUnit отчеты
└── data/                      # Тестовые данные
    ├── images/               # Тестовые изображения
    ├── documents/            # Тестовые документы
    └── databases/            # Тестовые БД
```

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
# Установка всех зависимостей для тестов
python test_suite/run_tests.py --install

# Или вручную
pip install pytest pytest-cov pytest-html pytest-xdist pytest-mock pytest-asyncio
pip install httpx selenium locust
```

### 2. Запуск всех тестов

```bash
# Запуск всех тестов
python test_suite/run_tests.py --all

# Или по типам
python test_suite/run_tests.py --unit
python test_suite/run_tests.py --integration
python test_suite/run_tests.py --security
python test_suite/run_tests.py --performance
python test_suite/run_tests.py --e2e
```

### 3. Дымовые тесты

```bash
# Быстрая проверка основных функций
python test_suite/run_tests.py --smoke
```

## 📊 Типы тестов

### Unit тесты (`unit/`)

Тестирование отдельных компонентов в изоляции.

**Покрытие:**
- Модели базы данных
- Сервисы и утилиты
- Валидация данных
- Бизнес-логика

**Запуск:**
```bash
python -m pytest test_suite/unit/ -v --cov=backend
```

### Интеграционные тесты (`integration/`)

Тестирование взаимодействия между компонентами.

**Покрытие:**
- API endpoints
- База данных
- Внешние сервисы
- Middleware

**Запуск:**
```bash
python -m pytest test_suite/integration/ -v --cov=backend
```

### E2E тесты (`e2e/`)

Тестирование полных пользовательских сценариев.

**Покрытие:**
- Пользовательские сценарии
- Админские сценарии
- Мобильная адаптивность
- Кроссбраузерное тестирование

**Запуск:**
```bash
python -m pytest test_suite/e2e/ -v
```

### Тесты безопасности (`security/`)

Проверка уязвимостей и безопасности.

**Покрытие:**
- XSS атаки
- SQL инъекции
- CSRF атаки
- Path traversal
- Аутентификация и авторизация

**Запуск:**
```bash
python -m pytest test_suite/security/ -v
```

### Performance тесты (`performance/`)

Нагрузочное тестирование и проверка производительности.

**Покрытие:**
- Время отклика
- Пропускная способность
- Использование ресурсов
- Стресс-тестирование

**Запуск:**
```bash
python -m pytest test_suite/performance/ -v
```

## 🔧 Конфигурация

### pytest.ini

Основные настройки pytest:

```ini
[tool:pytest]
testpaths = test_suite
python_files = test_*.py *_test.py
addopts = -v --tb=short --cov=backend --cov-report=html
markers =
    unit: Unit тесты
    integration: Интеграционные тесты
    e2e: End-to-end тесты
    security: Тесты безопасности
    performance: Performance тесты
```

### conftest.py

Глобальные фикстуры и конфигурация:

- Тестовая база данных
- Тестовый клиент FastAPI
- Фикстуры аутентификации
- Моки внешних сервисов

## 📈 Отчеты

### Покрытие кода

```bash
# Генерация отчета покрытия
python -m pytest --cov=backend --cov-report=html:test_suite/reports/coverage
```

### HTML отчеты

```bash
# Генерация HTML отчетов
python -m pytest --html=test_suite/reports/report.html --self-contained-html
```

### JUnit отчеты

```bash
# Генерация JUnit отчетов для CI/CD
python -m pytest --junitxml=test_suite/reports/junit.xml
```

## 🎯 Маркеры тестов

Используйте маркеры для запуска определенных типов тестов:

```bash
# Только unit тесты
pytest -m unit

# Только интеграционные тесты
pytest -m integration

# Только тесты безопасности
pytest -m security

# Только performance тесты
pytest -m performance

# Только E2E тесты
pytest -m e2e

# Медленные тесты
pytest -m slow

# Дымовые тесты
pytest -m smoke
```

## 🔄 CI/CD интеграция

### GitHub Actions

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.12
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          python test_suite/run_tests.py --install
      - name: Run tests
        run: python test_suite/run_tests.py --all
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

### GitLab CI

```yaml
test:
  stage: test
  image: python:3.12
  script:
    - pip install -r requirements.txt
    - python test_suite/run_tests.py --install
    - python test_suite/run_tests.py --all
  artifacts:
    reports:
      junit: test_suite/reports/junit.xml
    paths:
      - test_suite/reports/
```

## 🛠 Утилиты

### Генерация тестовых данных

```python
# Создание тестовых пользователей
python -c "
from test_suite.fixtures.test_data import sample_users
print(sample_users)
"
```

### Очистка тестовых данных

```bash
# Очистка временных файлов
find test_suite/ -name "*.tmp" -delete
find test_suite/ -name "__pycache__" -exec rm -rf {} +
```

## 📋 Чек-лист тестирования

### Перед коммитом

- [ ] Unit тесты проходят
- [ ] Интеграционные тесты проходят
- [ ] Покрытие кода > 80%
- [ ] Нет критических уязвимостей безопасности

### Перед релизом

- [ ] Все тесты проходят
- [ ] E2E тесты проходят
- [ ] Performance тесты в норме
- [ ] Тесты безопасности проходят
- [ ] Документация обновлена

## 🐛 Отладка тестов

### Включение отладочной информации

```bash
# Подробный вывод
pytest -v -s

# Остановка на первой ошибке
pytest -x

# Максимальное количество ошибок
pytest --maxfail=5
```

### Логирование

```bash
# Включение логов
pytest --log-cli-level=DEBUG

# Сохранение логов в файл
pytest --log-file=test.log --log-file-level=DEBUG
```

## 📚 Дополнительные ресурсы

- [Документация pytest](https://docs.pytest.org/)
- [Документация FastAPI тестирования](https://fastapi.tiangolo.com/tutorial/testing/)
- [Руководство по тестированию безопасности](https://owasp.org/www-project-web-security-testing-guide/)
- [Performance тестирование](https://locust.io/)

## 🤝 Вклад в тестирование

1. Создавайте тесты для нового функционала
2. Обновляйте тесты при изменении API
3. Добавляйте тесты безопасности для новых endpoints
4. Обновляйте документацию тестов

## 📞 Поддержка

При возникновении проблем с тестами:

1. Проверьте логи в `test_suite/reports/`
2. Убедитесь, что все зависимости установлены
3. Проверьте конфигурацию в `conftest.py`
4. Создайте issue с описанием проблемы 