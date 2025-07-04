from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
from pathlib import Path
from deep_translator import GoogleTranslator

router = APIRouter(prefix="/api/translate", tags=["auto-translation"])

# Модели данных
class TranslationRequest(BaseModel):
    text: str
    target_language: str
    source_language: str = "ru"

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    success: bool
    error: Optional[str] = None

class ArticleTranslationRequest(BaseModel):
    article_id: int
    target_languages: List[str] = ["en", "th", "zh"]
    auto_publish: bool = False

# Функции для автоматического перевода
async def auto_translate_article_content(article_data: Dict, target_langs: List[str]):
    """Автоматически переводит содержимое статьи"""
    
    try:
        translated_content = {}
        fields_to_translate = ['title', 'content', 'excerpt', 'meta_description']
        for field in fields_to_translate:
            if field in article_data and article_data[field]:
                original_text = article_data[field]
                if len(original_text) > 4000:
                    paragraphs = original_text.split('\n\n')
                    translated_paragraphs = {}
                    for lang in target_langs:
                        translated_parts = []
                        for paragraph in paragraphs:
                            if paragraph.strip():
                                try:
                                    translated_part = GoogleTranslator(source='ru', target=lang).translate(paragraph.strip())
                                    translated_parts.append(translated_part)
                                except Exception as e:
                                    print(f"Ошибка перевода параграфа: {e}")
                                    translated_parts.append(paragraph)
                            else:
                                translated_parts.append('')
                        translated_paragraphs[lang] = '\n\n'.join(translated_parts)
                    for lang in target_langs:
                        translated_content[f"{field}_{lang}"] = translated_paragraphs[lang]
                else:
                    for lang in target_langs:
                        try:
                            translated_text = GoogleTranslator(source='ru', target=lang).translate(original_text)
                            translated_content[f"{field}_{lang}"] = translated_text
                        except Exception as e:
                            print(f"Ошибка перевода {field}: {e}")
                            translated_content[f"{field}_{lang}"] = original_text
        return translated_content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка перевода: {str(e)}")

@router.post("/text", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """Переводит отдельный текст"""
    
    try:
        translated = GoogleTranslator(source=request.source_language, target=request.target_language).translate(request.text)
        return TranslationResponse(
            original_text=request.text,
            translated_text=translated,
            source_language=request.source_language,
            target_language=request.target_language,
            success=True
        )
    except Exception as e:
        return TranslationResponse(
            original_text=request.text,
            translated_text=request.text,
            source_language=request.source_language,
            target_language=request.target_language,
            success=False,
            error=str(e)
        )

@router.post("/article/{article_id}")
async def translate_article(
    article_id: int, 
    request: ArticleTranslationRequest, 
    background_tasks: BackgroundTasks
):
    """Переводит статью на указанные языки"""
    
    # Добавляем задачу в фон для перевода
    background_tasks.add_task(
        process_article_translation,
        article_id,
        request.target_languages,
        request.auto_publish
    )
    
    return {
        "message": f"Перевод статьи {article_id} добавлен в очередь",
        "target_languages": request.target_languages,
        "status": "processing"
    }

async def process_article_translation(
    article_id: int, 
    target_languages: List[str], 
    auto_publish: bool = False
):
    """Фоновая задача для перевода статьи"""
    
    try:
        # Здесь должна быть логика получения статьи из БД
        # Для примера используем mock данные
        
        article_data = {
            "id": article_id,
            "title": "Покупка недвижимости в Паттайе: полное руководство",
            "content": """
            Паттайя — один из самых популярных курортов Таиланда для покупки недвижимости. 
            Город предлагает широкий выбор объектов: от бюджетных студий до роскошных вилл.
            
            Основные преимущества покупки недвижимости в Паттайе:
            - Доступные цены по сравнению с Европой
            - Высокий туристический поток
            - Развитая инфраструктура
            - Близость к Бангкоку
            """,
            "excerpt": "Полное руководство по покупке недвижимости в Паттайе для иностранцев",
            "meta_description": "Узнайте все о покупке недвижимости в Паттайе: цены, документы, лучшие районы"
        }
        
        # Переводим контент
        translated_content = await auto_translate_article_content(article_data, target_languages)
        
        # Здесь должно быть сохранение в БД
        print(f"✅ Статья {article_id} переведена на языки: {', '.join(target_languages)}")
        
        # Создаем markdown файлы переводов
        for lang in target_languages:
            create_translated_markdown_file(article_id, article_data, translated_content, lang)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка перевода статьи {article_id}: {e}")
        return False

def create_translated_markdown_file(article_id: int, original_data: Dict, translated_content: Dict, language: str):
    """Создает markdown файл переведенной статьи"""
    
    articles_dir = Path("backend/articles/markdown")
    articles_dir.mkdir(parents=True, exist_ok=True)
    
    # Получаем переведенные поля
    title = translated_content.get(f"title_{language}", original_data.get("title", ""))
    content = translated_content.get(f"content_{language}", original_data.get("content", ""))
    excerpt = translated_content.get(f"excerpt_{language}", original_data.get("excerpt", ""))
    
    # Создаем содержимое файла
    markdown_content = f"""---
title: "{title}"
excerpt: "{excerpt}"
language: "{language}"
original_id: {article_id}
created_by: "auto_translation"
---

# {title}

{content}
"""
    
    # Имя файла
    filename = f"article-{article_id}-{language}.md"
    filepath = articles_dir / filename
    
    # Сохраняем файл
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"✅ Создан файл перевода: {filepath}")

@router.get("/queue/status")
async def get_translation_queue_status():
    """Получает статус очереди переводов"""
    
    # В реальном проекте здесь будет запрос к БД
    return {
        "total_in_queue": 0,
        "processing": 0,
        "completed_today": 5,
        "failed_today": 1,
        "available_languages": ["en", "th", "zh"],
        "translation_service": "Google Translate"
    }

@router.get("/languages")
async def get_supported_languages():
    """Возвращает список поддерживаемых языков"""
    
    return {
        "languages": [
            {"code": "en", "name": "English", "native": "English"},
            {"code": "th", "name": "Thai", "native": "ไทย"},
            {"code": "zh", "name": "Chinese", "native": "中文"},
            {"code": "ru", "name": "Russian", "native": "Русский"}
        ]
    } 