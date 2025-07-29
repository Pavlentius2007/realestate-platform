# Установка недостающих зависимостей

## Проблема
Некоторые функции админ-панели требуют дополнительные Python-модули:
- `psutil` - для мониторинга дискового пространства
- `pandas` - для экспорта пользователей в Excel
- `openpyxl` - для работы с Excel файлами

## Решение

### Способ 1: Установка всех зависимостей из requirements.txt
```bash
pip install -r requirements.txt
```

### Способ 2: Установка отдельных модулей
```bash
pip install psutil==5.9.6
pip install pandas==2.1.4  
pip install openpyxl==3.1.2
```

### Способ 3: Установка через python -m pip (если pip не работает)
```bash
python -m pip install psutil pandas openpyxl
```

## Проверка установки
После установки перезапустите сервер:
```bash
python backend/main.py
```

## Функциональность без зависимостей
Система будет работать и без этих модулей, но с ограниченной функциональностью:
- **Без psutil**: Информация о дисковом пространстве будет показывать "N/A"
- **Без pandas/openpyxl**: Экспорт пользователей в Excel будет недоступен

## Устранение неполадок

### PowerShell не выполняет команды pip
Если в PowerShell не работают команды pip, попробуйте:
1. Откройте PowerShell от имени администратора
2. Выполните: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
3. Попробуйте установку снова

### Ошибки прав доступа
Используйте флаг `--user`:
```bash
pip install --user psutil pandas openpyxl
``` 