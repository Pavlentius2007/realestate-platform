@echo off
echo Установка pandas и openpyxl...
echo.

REM Пробуем установить предкомпилированные версии
echo 1. Пробуем установить предкомпилированные версии...
python -m pip install --only-binary=all pandas==1.5.3 openpyxl==3.1.2
if %errorlevel% equ 0 (
    echo Успешно установлено!
    goto end
)

echo.
echo 2. Пробуем установить более старые версии...
python -m pip install pandas==1.3.5 openpyxl==3.0.10
if %errorlevel% equ 0 (
    echo Успешно установлено!
    goto end
)

echo.
echo 3. Пробуем установить базовые версии...
python -m pip install pandas openpyxl
if %errorlevel% equ 0 (
    echo Успешно установлено!
    goto end
)

echo.
echo 4. Пробуем установить только openpyxl (для Excel)...
python -m pip install openpyxl
if %errorlevel% equ 0 (
    echo Установлен только openpyxl
    goto end
)

echo.
echo Не удалось установить pandas. Функция экспорта будет недоступна.
echo Система будет работать без неё.

:end
echo.
echo Нажмите любую клавишу для выхода...
pause >nul 