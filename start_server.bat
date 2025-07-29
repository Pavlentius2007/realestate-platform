@echo off
echo 🚀 Запуск сервера Sianoro...
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не найден! Установите Python 3.8+
    pause
    exit /b 1
)

REM Проверяем наличие pip
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip не найден! Установите pip
    pause
    exit /b 1
)

REM Устанавливаем зависимости если нужно
if not exist "venv" (
    echo 📦 Создание виртуального окружения...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo 📥 Установка зависимостей...
    pip install -r requirements.txt
) else (
    echo 🔄 Активация виртуального окружения...
    call venv\Scripts\activate.bat
)

echo 🚀 Запуск сервера...
python run_server.py

pause 