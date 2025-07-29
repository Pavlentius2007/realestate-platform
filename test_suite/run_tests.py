#!/usr/bin/env python3
"""
Главный скрипт для запуска всех тестов
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any


class TestRunner:
    """Класс для запуска тестов"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_suite_dir = self.project_root / "test_suite"
        self.reports_dir = self.test_suite_dir / "reports"
        
        # Создаем директории для отчетов
        self.reports_dir.mkdir(exist_ok=True)
        
        # Цвета для вывода
        self.colors = {
            'green': '\033[92m',
            'red': '\033[91m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'bold': '\033[1m',
            'end': '\033[0m'
        }
    
    def print_header(self, message: str):
        """Вывод заголовка"""
        print(f"\n{self.colors['bold']}{self.colors['blue']}{'='*60}")
        print(f"  {message}")
        print(f"{'='*60}{self.colors['end']}\n")
    
    def print_success(self, message: str):
        """Вывод успешного сообщения"""
        print(f"{self.colors['green']}✅ {message}{self.colors['end']}")
    
    def print_error(self, message: str):
        """Вывод сообщения об ошибке"""
        print(f"{self.colors['red']}❌ {message}{self.colors['end']}")
    
    def print_warning(self, message: str):
        """Вывод предупреждения"""
        print(f"{self.colors['yellow']}⚠️  {message}{self.colors['end']}")
    
    def run_command(self, command: List[str], description: str) -> bool:
        """Запуск команды"""
        print(f"{self.colors['blue']}🔄 {description}...{self.colors['end']}")
        
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 минут таймаут
            )
            
            if result.returncode == 0:
                self.print_success(f"{description} завершено успешно")
                if result.stdout:
                    print(result.stdout)
                return True
            else:
                self.print_error(f"{description} завершено с ошибкой")
                if result.stderr:
                    print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            self.print_error(f"{description} превышен таймаут")
            return False
        except Exception as e:
            self.print_error(f"{description} ошибка: {e}")
            return False
    
    def run_unit_tests(self) -> bool:
        """Запуск unit тестов"""
        self.print_header("UNIT ТЕСТЫ")
        
        command = [
            sys.executable, "-m", "pytest",
            "test_suite/unit/",
            "-v",
            "--tb=short",
            "--cov=backend",
            "--cov-report=html:test_suite/reports/unit_coverage",
            "--cov-report=term-missing",
            "--junitxml=test_suite/reports/unit_tests.xml",
            "--html=test_suite/reports/unit_tests.html",
            "--self-contained-html"
        ]
        
        return self.run_command(command, "Unit тесты")
    
    def run_integration_tests(self) -> bool:
        """Запуск интеграционных тестов"""
        self.print_header("ИНТЕГРАЦИОННЫЕ ТЕСТЫ")
        
        command = [
            sys.executable, "-m", "pytest",
            "test_suite/integration/",
            "-v",
            "--tb=short",
            "--cov=backend",
            "--cov-report=html:test_suite/reports/integration_coverage",
            "--cov-report=term-missing",
            "--junitxml=test_suite/reports/integration_tests.xml",
            "--html=test_suite/reports/integration_tests.html",
            "--self-contained-html"
        ]
        
        return self.run_command(command, "Интеграционные тесты")
    
    def run_security_tests(self) -> bool:
        """Запуск тестов безопасности"""
        self.print_header("ТЕСТЫ БЕЗОПАСНОСТИ")
        
        command = [
            sys.executable, "-m", "pytest",
            "test_suite/security/",
            "-v",
            "--tb=short",
            "--junitxml=test_suite/reports/security_tests.xml",
            "--html=test_suite/reports/security_tests.html",
            "--self-contained-html"
        ]
        
        return self.run_command(command, "Тесты безопасности")
    
    def run_performance_tests(self) -> bool:
        """Запуск performance тестов"""
        self.print_header("PERFORMANCE ТЕСТЫ")
        
        command = [
            sys.executable, "-m", "pytest",
            "test_suite/performance/",
            "-v",
            "--tb=short",
            "--junitxml=test_suite/reports/performance_tests.xml",
            "--html=test_suite/reports/performance_tests.html",
            "--self-contained-html"
        ]
        
        return self.run_command(command, "Performance тесты")
    
    def run_e2e_tests(self) -> bool:
        """Запуск E2E тестов"""
        self.print_header("E2E ТЕСТЫ")
        
        # Проверяем, установлен ли Selenium
        try:
            import selenium
        except ImportError:
            self.print_warning("Selenium не установлен. Устанавливаем...")
            install_command = [sys.executable, "-m", "pip", "install", "selenium"]
            if not self.run_command(install_command, "Установка Selenium"):
                return False
        
        command = [
            sys.executable, "-m", "pytest",
            "test_suite/e2e/",
            "-v",
            "--tb=short",
            "--junitxml=test_suite/reports/e2e_tests.xml",
            "--html=test_suite/reports/e2e_tests.html",
            "--self-contained-html"
        ]
        
        return self.run_command(command, "E2E тесты")
    
    def run_smoke_tests(self) -> bool:
        """Запуск дымовых тестов"""
        self.print_header("ДЫМОВЫЕ ТЕСТЫ")
        
        command = [
            sys.executable, "-m", "pytest",
            "-m", "smoke",
            "-v",
            "--tb=short",
            "--junitxml=test_suite/reports/smoke_tests.xml",
            "--html=test_suite/reports/smoke_tests.html",
            "--self-contained-html"
        ]
        
        return self.run_command(command, "Дымовые тесты")
    
    def run_all_tests(self) -> bool:
        """Запуск всех тестов"""
        self.print_header("ПОЛНЫЙ ТЕСТ СЮИТ")
        
        start_time = time.time()
        
        # Запускаем тесты по порядку
        test_results = {
            "unit": self.run_unit_tests(),
            "integration": self.run_integration_tests(),
            "security": self.run_security_tests(),
            "performance": self.run_performance_tests(),
            "e2e": self.run_e2e_tests()
        }
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Выводим результаты
        self.print_header("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        
        all_passed = True
        for test_type, result in test_results.items():
            if result:
                self.print_success(f"{test_type.title()} тесты: ПРОЙДЕНЫ")
            else:
                self.print_error(f"{test_type.title()} тесты: ПРОВАЛЕНЫ")
                all_passed = False
        
        print(f"\n{self.colors['bold']}Общее время выполнения: {total_time:.2f} секунд{self.colors['end']}")
        
        if all_passed:
            self.print_success("Все тесты прошли успешно! 🎉")
        else:
            self.print_error("Некоторые тесты не прошли! ❌")
        
        return all_passed
    
    def generate_report(self):
        """Генерация общего отчета"""
        self.print_header("ГЕНЕРАЦИЯ ОТЧЕТА")
        
        report_file = self.reports_dir / "test_report.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Отчет о тестировании Sianoro\n\n")
            f.write(f"Дата: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Структура тестов\n\n")
            f.write("- **Unit тесты**: Тестирование отдельных компонентов\n")
            f.write("- **Интеграционные тесты**: Тестирование взаимодействия компонентов\n")
            f.write("- **Тесты безопасности**: Проверка уязвимостей\n")
            f.write("- **Performance тесты**: Нагрузочное тестирование\n")
            f.write("- **E2E тесты**: Тестирование пользовательских сценариев\n\n")
            
            f.write("## Файлы отчетов\n\n")
            f.write("- `unit_tests.html` - Отчет unit тестов\n")
            f.write("- `integration_tests.html` - Отчет интеграционных тестов\n")
            f.write("- `security_tests.html` - Отчет тестов безопасности\n")
            f.write("- `performance_tests.html` - Отчет performance тестов\n")
            f.write("- `e2e_tests.html` - Отчет E2E тестов\n")
            f.write("- `unit_coverage/` - Покрытие кода unit тестами\n")
            f.write("- `integration_coverage/` - Покрытие кода интеграционными тестами\n\n")
            
            f.write("## Запуск тестов\n\n")
            f.write("```bash\n")
            f.write("# Все тесты\n")
            f.write("python test_suite/run_tests.py --all\n\n")
            f.write("# Только unit тесты\n")
            f.write("python test_suite/run_tests.py --unit\n\n")
            f.write("# Только интеграционные тесты\n")
            f.write("python test_suite/run_tests.py --integration\n\n")
            f.write("# Только тесты безопасности\n")
            f.write("python test_suite/run_tests.py --security\n\n")
            f.write("# Только performance тесты\n")
            f.write("python test_suite/run_tests.py --performance\n\n")
            f.write("# Только E2E тесты\n")
            f.write("python test_suite/run_tests.py --e2e\n\n")
            f.write("# Дымовые тесты\n")
            f.write("python test_suite/run_tests.py --smoke\n")
            f.write("```\n")
        
        self.print_success(f"Отчет сгенерирован: {report_file}")
    
    def install_dependencies(self):
        """Установка зависимостей для тестов"""
        self.print_header("УСТАНОВКА ЗАВИСИМОСТЕЙ")
        
        dependencies = [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-html>=3.2.0",
            "pytest-xdist>=3.3.0",
            "pytest-mock>=3.11.0",
            "pytest-asyncio>=0.21.0",
            "httpx>=0.25.0",
            "selenium>=4.15.0",
            "locust>=2.17.0"
        ]
        
        for dep in dependencies:
            command = ["pip", "install", dep]
            if not self.run_command(command, f"Установка {dep}"):
                return False
        
        return True


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description="Запуск тестов Sianoro")
    parser.add_argument("--all", action="store_true", help="Запустить все тесты")
    parser.add_argument("--unit", action="store_true", help="Запустить только unit тесты")
    parser.add_argument("--integration", action="store_true", help="Запустить только интеграционные тесты")
    parser.add_argument("--security", action="store_true", help="Запустить только тесты безопасности")
    parser.add_argument("--performance", action="store_true", help="Запустить только performance тесты")
    parser.add_argument("--e2e", action="store_true", help="Запустить только E2E тесты")
    parser.add_argument("--smoke", action="store_true", help="Запустить дымовые тесты")
    parser.add_argument("--install", action="store_true", help="Установить зависимости")
    parser.add_argument("--report", action="store_true", help="Сгенерировать отчет")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Установка зависимостей
    if args.install:
        if not runner.install_dependencies():
            sys.exit(1)
        return
    
    # Генерация отчета
    if args.report:
        runner.generate_report()
        return
    
    # Запуск тестов
    success = True
    
    if args.all:
        success = runner.run_all_tests()
    elif args.unit:
        success = runner.run_unit_tests()
    elif args.integration:
        success = runner.run_integration_tests()
    elif args.security:
        success = runner.run_security_tests()
    elif args.performance:
        success = runner.run_performance_tests()
    elif args.e2e:
        success = runner.run_e2e_tests()
    elif args.smoke:
        success = runner.run_smoke_tests()
    else:
        # По умолчанию запускаем все тесты
        success = runner.run_all_tests()
    
    # Генерируем отчет
    runner.generate_report()
    
    # Возвращаем код выхода
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 