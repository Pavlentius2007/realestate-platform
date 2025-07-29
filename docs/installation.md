# 📦 Установка Транскрибатора

## Системные требования

### Операционная система
- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 18.04+, CentOS 7+)

### Python
- Python 3.10 или выше
- pip (менеджер пакетов Python)

### Дополнительные требования
- FFmpeg (для обработки аудио)
- Минимум 4 GB RAM
- 2 GB свободного места на диске

## Пошаговая установка

### 1. Установка Python

#### Windows
1. Скачайте Python с [python.org](https://www.python.org/downloads/)
2. При установке отметьте "Add Python to PATH"
3. Проверьте установку:
   ```bash
   python --version
   pip --version
   ```

#### macOS
```bash
# Через Homebrew
brew install python

# Или скачайте с python.org
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip
```

### 2. Установка FFmpeg

#### Windows
```bash
# Через Chocolatey
choco install ffmpeg

# Или скачайте с официального сайта
# https://ffmpeg.org/download.html
```

#### macOS
```bash
brew install ffmpeg
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg
```

### 3. Клонирование репозитория

```bash
git clone https://github.com/your-username/audio-transcriber.git
cd audio-transcriber
```

### 4. Создание виртуального окружения

```bash
# Создание виртуального окружения
python -m venv venv

# Активация (Windows)
venv\Scripts\activate

# Активация (macOS/Linux)
source venv/bin/activate
```

### 5. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 6. Проверка установки

```bash
python src/transcriber.py --help
```

## Альтернативные способы установки

### Установка через pip

```bash
pip install audio-transcriber
```

### Установка в режиме разработки

```bash
pip install -e .
```

## Проверка работоспособности

### Тест зависимостей
```bash
python -c "import whisper; print('Whisper установлен')"
python -c "import librosa; print('Librosa установлен')"
python -c "import pydub; print('Pydub установлен')"
```

### Тест FFmpeg
```bash
ffmpeg -version
```

### Тест транскрибатора
```bash
python src/transcriber.py --file test_audio.mp3 --language auto --output-format txt
```

## Устранение проблем

### Ошибка "FFmpeg not found"
1. Убедитесь что FFmpeg установлен
2. Добавьте FFmpeg в PATH
3. Перезапустите терминал

### Ошибка "CUDA not available"
- Это нормально, Whisper будет работать на CPU
- Для ускорения установите CUDA и PyTorch с поддержкой GPU

### Ошибка "Out of memory"
- Используйте модель меньшего размера (tiny, base)
- Обрабатывайте файлы по частям
- Увеличьте объем RAM

### Медленная работа
- Используйте GPU если доступен
- Используйте модель меньшего размера
- Закройте другие приложения

## Обновление

```bash
# Обновление из репозитория
git pull origin main
pip install -r requirements.txt --upgrade

# Обновление через pip
pip install audio-transcriber --upgrade
```

## Удаление

```bash
# Удаление пакета
pip uninstall audio-transcriber

# Удаление виртуального окружения
deactivate
rm -rf venv  # Linux/macOS
# или
rmdir /s venv  # Windows
``` 