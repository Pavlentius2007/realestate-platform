#!/usr/bin/env python3
"""
Тесты для транскрибатора
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Добавляем src в путь для импорта
sys.path.append(str(Path(__file__).parent.parent / "src"))

from utils import validate_file, create_output_dir, format_file_size, format_duration


class TestTranscriber(unittest.TestCase):
    """Тесты для транскрибатора"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Очистка после каждого теста"""
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def test_validate_file_nonexistent(self):
        """Тест валидации несуществующего файла"""
        result = validate_file("nonexistent_file.mp3")
        self.assertFalse(result)
        
    def test_validate_file_unsupported_format(self):
        """Тест валидации неподдерживаемого формата"""
        # Создаем временный файл с неподдерживаемым форматом
        temp_file = os.path.join(self.temp_dir, "test.txt")
        with open(temp_file, 'w') as f:
            f.write("test")
            
        result = validate_file(temp_file)
        self.assertFalse(result)
        
    def test_create_output_dir(self):
        """Тест создания директории для вывода"""
        test_dir = os.path.join(self.temp_dir, "output")
        result = create_output_dir(test_dir)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_dir))
        
    def test_format_file_size(self):
        """Тест форматирования размера файла"""
        # Тестируем разные размеры
        self.assertEqual(format_file_size(0), "0 B")
        self.assertEqual(format_file_size(1024), "1.00 KB")
        self.assertEqual(format_file_size(1024 * 1024), "1.00 MB")
        self.assertEqual(format_file_size(1024 * 1024 * 1024), "1.00 GB")
        
    def test_format_duration(self):
        """Тест форматирования длительности"""
        # Тестируем разные длительности
        self.assertEqual(format_duration(30), "30.0 сек")
        self.assertEqual(format_duration(90), "1 мин 30 сек")
        self.assertEqual(format_duration(3661), "1 ч 1 мин 1 сек")
        
    def test_validate_file_valid(self):
        """Тест валидации валидного файла"""
        # Создаем временный файл с поддерживаемым форматом
        temp_file = os.path.join(self.temp_dir, "test.mp3")
        with open(temp_file, 'w') as f:
            f.write("test audio content")
            
        result = validate_file(temp_file)
        self.assertTrue(result)
        
    def test_validate_file_empty(self):
        """Тест валидации пустого файла"""
        # Создаем пустой файл
        temp_file = os.path.join(self.temp_dir, "empty.mp3")
        with open(temp_file, 'w') as f:
            pass  # Создаем пустой файл
            
        result = validate_file(temp_file)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main() 