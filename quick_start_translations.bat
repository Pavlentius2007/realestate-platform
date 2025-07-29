@echo off
echo ================================================
echo 🚀 БЫСТРЫЙ СТАРТ СИСТЕМЫ ПЕРЕВОДОВ
echo ================================================

echo.
echo 📦 Шаг 1: Установка зависимостей...
call install_dependencies.bat

echo.
echo 🗄️ Шаг 2: Создание SQL настроек...
python auto_translate.py

echo.
echo ✅ Шаг 3: Тестирование системы...
python test_auto_translate.py

echo.
echo 🚀 Шаг 4: Запуск сервера...
echo.
echo 💡 Теперь:
echo    1. Выполните в PGAdmin4: setup_translation_hooks.sql
echo    2. Сервер готов к запуску: python run_server.py
echo    3. Админка переводов: http://localhost:8002/admin/auto-translate
echo.
echo 🎉 СИСТЕМА АВТОПЕРЕВОДОВ ГОТОВА!
echo.
pause 