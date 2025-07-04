#!/bin/bash

echo "🚀 Запуск сервера Sianoro..."
echo ""

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден! Установите Python 3.8+"
    exit 1
fi

# Проверяем наличие pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 не найден! Установите pip3"
    exit 1
fi

# Создаем виртуальное окружение если его нет
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📥 Установка зависимостей..."
    pip install -r requirements.txt
else
    echo "🔄 Активация виртуального окружения..."
    source venv/bin/activate
fi

echo "🚀 Запуск сервера..."
python3 run_server.py 