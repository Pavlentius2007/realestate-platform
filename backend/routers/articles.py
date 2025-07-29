from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from backend.config.templates import templates
import os
import markdown
import frontmatter
from pathlib import Path
# Используем современную систему переводов через ModernI18nMiddleware
from backend.fix_i18n_modern import inject_translator_to_templates

router = APIRouter()

ARTICLES_PATH = Path(__file__).resolve().parent.parent / "articles" / "markdown"

def load_articles():
    """Загрузка всех статей с метаданными"""
    articles = []
    if not ARTICLES_PATH.exists():
        return articles
    
    for file_path in ARTICLES_PATH.glob("*.md"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # Проверяем, опубликована ли статья
            if not post.get("published", True):
                continue
                
            articles.append({
                "slug": post.get("slug", file_path.stem),
                "title": post.get("title", file_path.stem),
                "excerpt": post.get("excerpt", ""),
                "category": post.get("category", "tips"),
                "featured_image": post.get("featured_image", None),
                "created_at": post.get("created_at", ""),
                "updated_at": post.get("updated_at", "")
            })
        except Exception as e:
            print(f"Ошибка загрузки файла {file_path}: {e}")
            continue
    
    return sorted(articles, key=lambda x: x.get("updated_at", ""), reverse=True)

def load_article_by_slug(slug: str):
    """Загрузка одной статьи по slug"""
    file_path = ARTICLES_PATH / f"{slug}.md"
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        # Проверяем, опубликована ли статья
        if not post.get("published", True):
            return None
        
        # Преобразуем markdown в HTML
        html_content = markdown.markdown(post.content, extensions=['codehilite', 'fenced_code'])
        
        return {
            "slug": post.get("slug", slug),
            "title": post.get("title", slug),
            "excerpt": post.get("excerpt", ""),
            "category": post.get("category", "tips"),
            "featured_image": post.get("featured_image", None),
            "content": html_content,
            "created_at": post.get("created_at", ""),
            "updated_at": post.get("updated_at", "")
        }
    except Exception as e:
        print(f"Ошибка загрузки статьи {slug}: {e}")
        return None

# 👉 Главная страница со списком статей
@router.get("/articles", response_class=HTMLResponse)
async def articles_page(request: Request, lang: str):
    # Принудительная инжекция переводчика (страховка)
    inject_translator_to_templates(templates, request)
    
    articles = load_articles()
    return templates.TemplateResponse("articles.html", {
        "request": request, 
        "lang": lang, 
        "articles": articles
    })

# 👉 Просмотр одной статьи
@router.get("/articles/{slug}", response_class=HTMLResponse)
def show_article(request: Request, slug: str, lang: str):
    # Принудительная инжекция переводчика (страховка)
    inject_translator_to_templates(templates, request)
    
    article = load_article_by_slug(slug)
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    
    articles = load_articles()  # Для бокового меню
    
    return templates.TemplateResponse("articles.html", {
        "request": request, 
        "lang": lang,
        "article": article,
        "articles": articles
    })
