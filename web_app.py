#!/usr/bin/env python3
"""
Веб-приложение для транскрибации аудио
Современный интерфейс для загрузки и обработки аудиофайлов
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import uvicorn
import os
import uuid
import asyncio
from pathlib import Path
import logging
from typing import Optional
import json

# Импорты для транскрибации
from src.whisper_handler import WhisperHandler
from src.audio_processor import AudioProcessor
from src.utils import setup_logging

# Настройка логирования
logger = setup_logging("transcriber_web")

# Создаем директории для загрузок и результатов
UPLOAD_DIR = Path("uploads")
RESULTS_DIR = Path("results")
UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Инициализация FastAPI
app = FastAPI(
    title="Аудио Транскрибатор",
    description="Современный веб-интерфейс для транскрибации аудиофайлов",
    version="1.0.0"
)

# Подключение статических файлов и шаблонов
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Инициализация обработчиков
whisper_handler = WhisperHandler()
audio_processor = AudioProcessor()

# Хранилище задач
tasks = {}

class TranscriptionTask:
    def __init__(self, task_id: str, filename: str):
        self.task_id = task_id
        self.filename = filename
        self.status = "pending"  # pending, processing, completed, error
        self.progress = 0
        self.result_path = None
        self.error_message = None
        self.language = None
        self.model = None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Главная страница с интерфейсом загрузки"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: str = Form("auto"),
    model: str = Form("base"),
    output_format: str = Form("txt")
):
    """Загрузка файла и запуск транскрибации"""
    
    # Проверяем формат файла
    allowed_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.ogg', '.webm'}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Неподдерживаемый формат файла. Разрешены: {', '.join(allowed_extensions)}"
        )
    
    # Создаем уникальный ID задачи
    task_id = str(uuid.uuid4())
    
    # Сохраняем файл
    file_path = UPLOAD_DIR / f"{task_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Создаем задачу
    task = TranscriptionTask(task_id, file.filename)
    task.language = language
    task.model = model
    tasks[task_id] = task
    
    # Запускаем обработку в фоне
    background_tasks.add_task(
        process_transcription, 
        task_id, 
        str(file_path), 
        language, 
        model, 
        output_format
    )
    
    return JSONResponse({
        "task_id": task_id,
        "message": "Файл загружен, начинаем транскрибацию",
        "status": "pending"
    })

async def process_transcription(
    task_id: str, 
    file_path: str, 
    language: str, 
    model: str, 
    output_format: str
):
    """Обработка транскрибации в фоновом режиме"""
    task = tasks.get(task_id)
    if not task:
        return
    
    try:
        task.status = "processing"
        task.progress = 10
        
        # Обрабатываем аудио
        logger.info(f"Начинаем обработку файла: {file_path}")
        audio_data = audio_processor.load_audio(file_path)
        
        if audio_data is None:
            raise Exception("Не удалось загрузить аудиофайл")
        
        task.progress = 30
        
        # Транскрибируем
        logger.info(f"Транскрибируем с параметрами: язык={language}, модель={model}")
        result = whisper_handler.transcribe(audio_data, language, model)
        
        if result is None:
            raise Exception("Ошибка транскрибации")
        
        task.progress = 70
        
        # Сохраняем результат
        output_filename = f"{task_id}_transcript.{output_format}"
        output_path = RESULTS_DIR / output_filename
        
        if output_format == "txt":
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result["text"])
        elif output_format == "srt":
            whisper_handler.save_srt(result, output_path)
        elif output_format == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        
        task.result_path = str(output_path)
        task.status = "completed"
        task.progress = 100
        
        logger.info(f"Транскрибация завершена: {output_path}")
        
    except Exception as e:
        logger.error(f"Ошибка обработки задачи {task_id}: {e}")
        task.status = "error"
        task.error_message = str(e)

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """Получение статуса задачи"""
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    response = {
        "task_id": task_id,
        "status": task.status,
        "progress": task.progress,
        "filename": task.filename
    }
    
    if task.status == "completed":
        response["download_url"] = f"/download/{task_id}"
        response["result_path"] = task.result_path
    
    if task.status == "error":
        response["error"] = task.error_message
    
    return JSONResponse(response)

@app.get("/download/{task_id}")
async def download_result(task_id: str):
    """Скачивание результата"""
    task = tasks.get(task_id)
    if not task or task.status != "completed":
        raise HTTPException(status_code=404, detail="Результат не найден")
    
    if not task.result_path or not os.path.exists(task.result_path):
        raise HTTPException(status_code=404, detail="Файл результата не найден")
    
    return FileResponse(
        task.result_path,
        filename=f"transcript_{task.filename}.{Path(task.result_path).suffix}",
        media_type="application/octet-stream"
    )

@app.get("/tasks")
async def list_tasks():
    """Список всех задач"""
    return JSONResponse({
        "tasks": [
            {
                "task_id": task.task_id,
                "filename": task.filename,
                "status": task.status,
                "progress": task.progress
            }
            for task in tasks.values()
        ]
    })

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Удаление задачи и файлов"""
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    # Удаляем файлы
    if task.result_path and os.path.exists(task.result_path):
        os.remove(task.result_path)
    
    # Удаляем задачу из памяти
    del tasks[task_id]
    
    return JSONResponse({"message": "Задача удалена"})

if __name__ == "__main__":
    uvicorn.run(
        "web_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 