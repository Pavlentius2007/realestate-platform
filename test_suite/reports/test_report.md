# Отчет о тестировании Sianoro

Дата: 2025-07-12 21:57:53

## Структура тестов

- **Unit тесты**: Тестирование отдельных компонентов
- **Интеграционные тесты**: Тестирование взаимодействия компонентов
- **Тесты безопасности**: Проверка уязвимостей
- **Performance тесты**: Нагрузочное тестирование
- **E2E тесты**: Тестирование пользовательских сценариев

## Файлы отчетов

- `unit_tests.html` - Отчет unit тестов
- `integration_tests.html` - Отчет интеграционных тестов
- `security_tests.html` - Отчет тестов безопасности
- `performance_tests.html` - Отчет performance тестов
- `e2e_tests.html` - Отчет E2E тестов
- `unit_coverage/` - Покрытие кода unit тестами
- `integration_coverage/` - Покрытие кода интеграционными тестами

## Запуск тестов

```bash
# Все тесты
python test_suite/run_tests.py --all

# Только unit тесты
python test_suite/run_tests.py --unit

# Только интеграционные тесты
python test_suite/run_tests.py --integration

# Только тесты безопасности
python test_suite/run_tests.py --security

# Только performance тесты
python test_suite/run_tests.py --performance

# Только E2E тесты
python test_suite/run_tests.py --e2e

# Дымовые тесты
python test_suite/run_tests.py --smoke
```
