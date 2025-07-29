@echo off
echo ================================================
echo 🚀 Установка зависимостей для Realestate Platform
echo ================================================

echo.
echo 📦 Установка всех зависимостей из requirements.txt...
pip install -r requirements.txt

echo.
echo ✅ Проверка установленных пакетов...
pip show fastapi
pip show googletrans

echo.
echo 🎉 Установка завершена!
echo.
echo 💡 Теперь можете запустить:
echo    python auto_translate.py
echo    python run_server.py
echo.
pause 