from fastapi import FastAPI, Request, HTTPException, Depends, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from typing import Optional, List
from urllib.parse import urlparse, urlunparse
import json
import os

try:
    # Попытка импорта с backend. (когда запускаем из корня)
    from backend.database import engine, Base, SessionLocal, get_db
    from backend.routers import admin, user_tools, stats, projects, submit_property, rental_request, favorites, submit_rent, analytics, crm
    from backend.routers.articles import router as articles_router
    from backend.routers.properties import router as properties_router
    from backend.routers.auto_translation import router as auto_translation_router
    from backend.models.property import Property
    from backend.models.property_image import PropertyImage
    from backend.config.settings import settings
    from backend.utils.config_utils import get_config_for_template, get_analytics_scripts
except ImportError:
    # Относительные импорты (когда запускаем из backend/)
    from database import engine, Base, SessionLocal, get_db
    from routers import admin, user_tools, stats, projects, submit_property, rental_request, favorites, submit_rent, analytics, crm
    from routers.articles import router as articles_router
    from routers.properties import router as properties_router
    from routers.auto_translation import router as auto_translation_router
    from models.property import Property
    from models.property_image import PropertyImage
    from config.settings import settings
    from utils.config_utils import get_config_for_template, get_analytics_scripts
from sqlalchemy.orm import Session, joinedload
import markdown
import frontmatter
try:
    from backend.config.i18n import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, LANGUAGE_COOKIE_NAME
    from backend.config.templates import templates
    from backend.fix_i18n_modern import ModernI18n, ModernI18nMiddleware, i18n
except ImportError:
    from config.i18n import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, LANGUAGE_COOKIE_NAME
    from config.templates import templates
    from fix_i18n_modern import ModernI18n, ModernI18nMiddleware, i18n

# 📁 Базовая директория и шаблоны
# Определяем корневую директорию проекта независимо от текущей рабочей директории
CURRENT_FILE = Path(__file__).resolve()
if CURRENT_FILE.parent.name == "backend":
    # Запуск из backend директории
    BASE_DIR = CURRENT_FILE.parent.parent  # realestate-platform
else:
    # Запуск из корневой директории
    BASE_DIR = CURRENT_FILE.parent  # realestate-platform

TEMPLATES_DIR = BASE_DIR / "backend" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.globals["supported_languages"] = SUPPORTED_LANGUAGES
templates.env.globals['now'] = datetime.now

# 🌍 Импорт конфигурации и инициализация i18n
try:
    from backend.config.i18n import (
        LANGUAGE_COOKIE_MAX_AGE,
        LANGUAGE_SESSION_KEY
    )
except ImportError:
    from config.i18n import (
        LANGUAGE_COOKIE_MAX_AGE,
        LANGUAGE_SESSION_KEY
    )

def inject_translator_to_templates(templates: Jinja2Templates, request: Request):
    """Добавляет функцию перевода и конфигурацию в шаблоны"""
    lang = i18n.get_user_language(request)
    
    def _(key: str, **kwargs) -> str:
        return i18n.translate(key, lang, **kwargs)
    
    templates.env.globals['_'] = _
    templates.env.globals['lang'] = lang
    templates.env.globals['supported_languages'] = SUPPORTED_LANGUAGES
    
    # Добавляем конфигурацию для white label
    config = get_config_for_template()
    templates.env.globals['config'] = config
    templates.env.globals['analytics_scripts'] = get_analytics_scripts()

# 🚀 Инициализация FastAPI
app = FastAPI(debug=True)

# 🛡 Middleware - порядок важен!
# 1. SessionMiddleware должен быть первым
app.add_middleware(
    SessionMiddleware,
    secret_key="super-sianoro-key",
    max_age=LANGUAGE_COOKIE_MAX_AGE,
    same_site="lax",
    https_only=False
)

# 2. CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. ModernI18nMiddleware - после всех остальных
app.add_middleware(ModernI18nMiddleware, templates=templates)

# 🔼 Статические файлы
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.mount("/css", StaticFiles(directory=str(BASE_DIR / "static" / "css")), name="css")
app.mount("/js", StaticFiles(directory=str(BASE_DIR / "static" / "js")), name="js")
app.mount("/images", StaticFiles(directory=str(BASE_DIR / "static" / "images")), name="images")
app.mount("/locales", StaticFiles(directory=str(BASE_DIR / "locales")), name="locales")

# 🌍 Загрузка переводов
i18n.load_translations()  # Принудительная перезагрузка переводов при старте

# 🌍 Смена языка - ДОЛЖЕН БЫТЬ ПЕРЕД ВСЕМИ РОУТЕРАМИ!
@app.get("/lang/{lang_code}")
async def switch_language(request: Request, lang_code: str):
    """Переключает язык интерфейса с сохранением в сессии и cookie"""
    
    # Проверяем, что язык поддерживается
    if lang_code not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported language. Supported: {', '.join(SUPPORTED_LANGUAGES.keys())}"
        )
    
    # 1. Сохраняем в сессии
    try:
        request.session[LANGUAGE_SESSION_KEY] = lang_code
        print(f"🌍 set_language_in_session: установлен язык {lang_code}")
    except Exception as e:
        print(f"⚠️ Ошибка сохранения в сессии: {e}")
    
    # 2. Определяем URL для редиректа
    referer = request.headers.get("referer")
    if not referer:
        return RedirectResponse(f"/{lang_code}", status_code=302)
    
    # Парсим referer URL чтобы заменить язык
    parsed = urlparse(referer)
    path_parts = parsed.path.strip('/').split('/')
    
    # Если первая часть - код языка, заменяем его
    if path_parts and path_parts[0] in SUPPORTED_LANGUAGES:
        path_parts[0] = lang_code
    else:
        # Если языка нет в пути, добавляем
        path_parts.insert(0, lang_code)
    
    # Собираем новый URL с сохранением query параметров
    new_path = '/' + '/'.join(path_parts)
    new_url = urlunparse(parsed._replace(path=new_path))
    
    # Проверяем AJAX запрос
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if is_ajax:
        return {"success": True, "redirect_url": new_url}
    
    # Создаем редирект с установкой cookie
    response = RedirectResponse(url=new_url, status_code=302)
    response.set_cookie(
        key=LANGUAGE_COOKIE_NAME,
        value=lang_code,
        max_age=LANGUAGE_COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=request.url.scheme == "https"
    )
    
    return response

# 🔌 Подключение роутеров
app.include_router(admin.router)
app.include_router(analytics.router)
app.include_router(crm.router)
app.include_router(auto_translation_router, prefix="/api/translate", tags=["Auto Translation"])
app.include_router(rental_request.router)
app.include_router(submit_property.router)
app.include_router(submit_rent.router)
app.include_router(user_tools.router)
app.include_router(stats.router, prefix="/stats", tags=["Stats"])
app.include_router(properties_router, prefix="/{lang}/properties", tags=["Properties"])
app.include_router(projects.router, prefix="/{lang}")
app.include_router(favorites.router, prefix="/{lang}", tags=["Favorites"])
app.include_router(articles_router, prefix="/{lang}", tags=["Articles"])

# 📄 Маршруты страниц
@app.get("/{lang}")
async def home(request: Request, lang: str):
    """Главная страница"""
    if lang not in SUPPORTED_LANGUAGES:
        return RedirectResponse(url=f"/{DEFAULT_LANGUAGE}{request.url.path}")
    
    # Принудительная инжекция переводчика (страховка)
    inject_translator_to_templates(templates, request)
    
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/{lang}/rent", response_class=HTMLResponse)
async def rent(request: Request, lang: str):
    """Страница аренды"""
    if lang not in SUPPORTED_LANGUAGES:
        return RedirectResponse(url=f"/{DEFAULT_LANGUAGE}/rent")
    
    # Принудительная инжекция переводчика (страховка)
    inject_translator_to_templates(templates, request)
    
    return templates.TemplateResponse("rent.html", {"request": request})

@app.get("/{lang}/about", response_class=HTMLResponse)
def about(request: Request, lang: str):
    """О нас"""
    if lang not in SUPPORTED_LANGUAGES:
        return RedirectResponse(url=f"/{DEFAULT_LANGUAGE}/about")
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/{lang}/contacts", response_class=HTMLResponse)
def contacts_page(request: Request, lang: str):
    """Контакты"""
    if lang not in SUPPORTED_LANGUAGES:
        return RedirectResponse(url=f"/{DEFAULT_LANGUAGE}/contacts")
    return templates.TemplateResponse("contacts.html", {"request": request})

@app.get("/{lang}/privacy", response_class=HTMLResponse)
def privacy_policy(request: Request, lang: str):
    """Политика конфиденциальности"""
    if lang not in SUPPORTED_LANGUAGES:
        return RedirectResponse(url=f"/{DEFAULT_LANGUAGE}/privacy")
    return templates.TemplateResponse("legal/privacy.html", {"request": request})

@app.get("/{lang}/terms", response_class=HTMLResponse)
def terms_of_service(request: Request, lang: str):
    """Условия использования"""
    if lang not in SUPPORTED_LANGUAGES:
        return RedirectResponse(url=f"/{DEFAULT_LANGUAGE}/terms")
    return templates.TemplateResponse("legal/terms.html", {"request": request})

@app.get("/{lang}/ai-search", response_class=HTMLResponse)
def ai_search(request: Request, lang: str):
    """AI поиск"""
    if lang not in SUPPORTED_LANGUAGES:
        return RedirectResponse(url=f"/{DEFAULT_LANGUAGE}/ai-search")
    return templates.TemplateResponse("ai_search.html", {"request": request})

@app.get("/{lang}/ai-chat", response_class=HTMLResponse)
def ai_chat_page(request: Request, lang: str):
    """Страница умного ИИ-чата"""
    if lang not in SUPPORTED_LANGUAGES:
        return RedirectResponse(url=f"/{DEFAULT_LANGUAGE}/ai-chat")
    return templates.TemplateResponse("ai_chat.html", {"request": request})

@app.post("/{lang}/ai-chat")
def ai_chat_api(request: Request, lang: str, 
                message: str = Form(...),
                session_id: str = Form(None)):
    """API для обработки сообщений ИИ-чата"""
    try:
        from services.ai_assistant import RealEstateAIAssistant
        from database import SessionLocal
        
        # Создаем соединение с БД
        db = SessionLocal()
        
        try:
            # Инициализируем ИИ-помощника
            ai_assistant = RealEstateAIAssistant(db)
            
            # Обрабатываем сообщение
            ai_response, found_properties, session_id = ai_assistant.process_message(
                message, session_id
            )
            
            # Формируем список объектов для фронтенда
            properties_data = []
            for prop in found_properties:
                properties_data.append({
                    "id": prop.id,
                    "title": prop.title,
                    "price": prop.price,
                    "area": prop.area,
                    "bedrooms": prop.bedrooms,
                    "district": prop.district,
                    "location": prop.location,
                    "preview_image": prop.preview_image
                })
            
            return {
                "success": True,
                "response": ai_response,
                "properties": properties_data,
                "session_id": session_id
            }
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"Ошибка в ИИ-чате: {e}")
        return {
            "success": False,
            "response": "Извините, произошла ошибка. Попробуйте позже или обратитесь к нашим консультантам.",
            "properties": [],
            "session_id": session_id
        }

# 🏢 Страница объекта
@app.get("/{lang}/properties/{property_id}", response_class=HTMLResponse)
def property_detail(request: Request, lang: str, property_id: int, db: Session = Depends(get_db)):
    # Язык управляется автоматически через ModernI18nMiddleware
    
    # Принудительная инжекция переводчика (страховка)
    inject_translator_to_templates(templates, request)
    
    try:
        property = db.query(Property).options(joinedload(Property.images)).filter(Property.id == property_id).first()
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")

        related_properties = db.query(Property).filter(
            Property.district == property.district,
            Property.id != property.id
        ).limit(4).all()

        return templates.TemplateResponse("property_detail.html", {
            "request": request,
            "property": property,
            "related_properties": related_properties,
            "lang": lang
        })
    except Exception:
        import traceback
        traceback.print_exc()
        return HTMLResponse(content="Ошибка отображения объекта", status_code=500)

# 🔍 Поиск
@app.get("/{lang}/search", response_class=HTMLResponse)
def search(request: Request, lang: str, q: str = "", property_type: str = ""):
    # Язык управляется автоматически через ModernI18nMiddleware
    
    db = SessionLocal()
    query = db.query(Property)
    if q:
        query = query.filter(Property.title.ilike(f"%{q}%") | Property.description.ilike(f"%{q}%"))
    if property_type:
        query = query.filter(Property.type.ilike(f"%{property_type}%"))
    results = query.all()
    db.close()
    return templates.TemplateResponse("search_results.html", {
        "request": request, "results": results, "query": q, "property_type": property_type,
        "lang": lang
    })

@app.get("/{lang}/repair", response_class=HTMLResponse)
def repair_page(request: Request, lang: str):
    # Язык и переводчик доступны через ModernI18nMiddleware!
    return templates.TemplateResponse("repair.html", {"request": request, "lang": lang})

# 🛠 Создание таблиц
Base.metadata.create_all(bind=engine)

# 🔗 Корневые роуты без языковых префиксов (для удобства)
@app.get("/", response_class=HTMLResponse)
async def root_home(request: Request):
    return RedirectResponse(url="/ru", status_code=302)

@app.get("/new-builds-catalog", response_class=HTMLResponse)
async def root_new_builds(request: Request):
    return RedirectResponse(url="/ru/properties/new-builds", status_code=302)

@app.get("/projects-catalog", response_class=HTMLResponse)
async def root_projects_catalog(request: Request):
    return RedirectResponse(url="/ru/projects", status_code=302)

@app.get("/projects/{project_slug}", response_class=HTMLResponse)
async def root_project_detail(request: Request, project_slug: str):
    return RedirectResponse(url=f"/ru/projects/{project_slug}", status_code=302)

@app.post("/{lang}/ai-search", response_class=HTMLResponse)
def ai_search_post(request: Request, lang: str,
    budget: int = Form(None),
    area_from: int = Form(None),
    area_to: int = Form(None),
    district: str = Form(""),
    property_type: str = Form(""),
    bedrooms: str = Form(""),
    floor: str = Form(""),
    furnished: str = Form(""),
    view: str = Form(""),
    level: str = Form(""),
    pets: str = Form(""),
    pool: str = Form(""),
    new_or_secondary: str = Form(""),
    purpose: str = Form(""),
    infra_school: str = Form(""),
    infra_beach: str = Form(""),
    infra_mall: str = Form(""),
    infra_market: str = Form(""),
    infra_hospital: str = Form(""),
    infra_gym: str = Form(""),
):
    # Язык управляется автоматически через ModernI18nMiddleware
    db = SessionLocal()
    query = db.query(Property)
    if budget:
        query = query.filter(Property.price <= budget)
    if area_from:
        query = query.filter(Property.area >= area_from)
    if area_to:
        query = query.filter(Property.area <= area_to)
    if district:
        query = query.filter(Property.district == district)
    if property_type:
        query = query.filter(Property.property_type == property_type)
    if bedrooms:
        try:
            min_bed = int(bedrooms[0])
            query = query.filter(Property.bedrooms >= min_bed)
        except:
            pass
    if furnished:
        query = query.filter(Property.furnished == furnished)
    if view:
        query = query.filter(Property.description.ilike(f"%{view}%"))
    if level:
        query = query.filter(Property.status == level)
    if pets == "Да":
        query = query.filter(Property.pets_allowed == True)
    if pets == "Нет":
        query = query.filter(Property.pets_allowed == False)
    if pool == "С бассейном":
        query = query.filter(Property.features.any("бассейн"))
    if pool == "Без бассейна":
        query = query.filter(~Property.features.any("бассейн"))
    if new_or_secondary == "Новостройка":
        query = query.filter(Property.property_type == "new")
    if new_or_secondary == "Вторичка":
        query = query.filter(Property.property_type != "new")
    # Инфраструктура (пример: ищем по description)
    infra_keywords = []
    if infra_school: infra_keywords.append("школа")
    if infra_beach: infra_keywords.append("пляж")
    if infra_mall: infra_keywords.append("ТЦ")
    if infra_market: infra_keywords.append("рынок")
    if infra_hospital: infra_keywords.append("госпиталь")
    if infra_gym: infra_keywords.append("спортзал")
    for kw in infra_keywords:
        query = query.filter(Property.description.ilike(f"%{kw}%"))
    results = query.all()
    db.close()
    # Переводчик автоматически доступен через middleware!
    explanation = "ИИ-подбор: фильтрация по вашим параметрам. В будущем здесь появится персонализированная рекомендация!"
    return templates.TemplateResponse("ai_search.html", {
        "request": request,
        "lang": lang,
        "results": results,
        "explanation": explanation
    })

# Функция для безопасного доступа к сессии
def get_session_language(request: Request) -> Optional[str]:
    """Безопасно получает язык из сессии"""
    try:
        if hasattr(request, 'session'):
            return request.session.get(LANGUAGE_SESSION_KEY)
    except Exception as e:
        print(f"⚠️ Ошибка доступа к сессии: {e}")
    return None

# Обновляем функцию определения языка
def get_preferred_language(request: Request) -> str:
    """Определяет предпочтительный язык пользователя"""
    
    # 1. Проверяем URL
    path = str(request.url.path)
    if path.startswith('/'):
        parts = path.strip('/').split('/')
        if parts and parts[0] in SUPPORTED_LANGUAGES:
            return parts[0]
    
    # 2. Проверяем сессию
    session_lang = get_session_language(request)
    if session_lang and session_lang in SUPPORTED_LANGUAGES:
        return session_lang
    
    # 3. Проверяем cookie
    cookie_lang = request.cookies.get(LANGUAGE_COOKIE_NAME)
    if cookie_lang and cookie_lang in SUPPORTED_LANGUAGES:
        return cookie_lang
    
    # 4. Проверяем заголовок Accept-Language
    accept_lang = request.headers.get("accept-language", "")
    if accept_lang:
        langs = accept_lang.split(",")
        for lang in langs:
            code = lang.split(";")[0].strip().lower()[:2]
            if code in SUPPORTED_LANGUAGES:
                return code
    
    return DEFAULT_LANGUAGE

@app.middleware("http")
async def add_ajax_header(request: Request, call_next):
    response = await call_next(request)
    # Проверяем, является ли запрос AJAX
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    
    # Для AJAX-запросов возвращаем только HTML-контент
    if is_ajax and isinstance(response, Response):
        response.headers["X-Is-Ajax"] = "true"
    
    return response

# 🚀 Запуск сервера
if __name__ == "__main__":
    import uvicorn
    import socket
    
    def find_free_port(start_port=8002):
        """Find a free port starting from the given port"""
        port = start_port
        while port < start_port + 10:  # Try 10 ports
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    return port
            except OSError:
                port += 1
        raise RuntimeError("Could not find a free port")
    
    try:
        # Создаем таблицы при запуске
        from database import create_tables
        print("📦 Создание таблиц БД...")
        create_tables()
        print("✅ Таблицы созданы успешно!")
        
        port = find_free_port()
        print("🚀 Запуск сервера Sianoro...")
        print(f"📍 Сайт: http://localhost:{port}/ru")
        print(f"🤖 ИИ-Чат: http://localhost:{port}/ru/ai-chat")
        print(f"📍 Админка: http://localhost:{port}/admin")
        print(f"🏗️ Добавить новостройку: http://localhost:{port}/admin/add-project")
        uvicorn.run(app, host="127.0.0.1", port=port)
    except Exception as e:
        print(f"Ошибка при запуске сервера: {e}")

# 👉 Поддержка /{lang}/admin: показываем ту же админку без редиректов, чтобы избежать циклов

from fastapi import Depends  # импорт для использования в функции ниже

@app.get("/{lang}/admin", response_class=HTMLResponse)
def admin_page_lang(request: Request, lang: str, db: Session = Depends(get_db)):
    """Отображает админку по адресу /{lang}/admin, без перенаправления"""

    # Инжектируем переводчик в шаблоны, используемые админкой
    try:
        from backend.config.templates import templates as admin_templates
    except ImportError:
        from config.templates import templates as admin_templates
    inject_translator_to_templates(admin_templates, request)

    # Админка не зависит от выбранного языка интерфейса, поэтому просто вызываем
    # оригинальный обработчик напрямую
    return admin.admin_page(request, db)

# Универсальный редирект всех внутренних страниц админки с языковым префиксом
@app.get("/{lang}/admin/{rest_path:path}")
async def admin_subpath_redirect(lang: str, rest_path: str):
    """Перенаправляет /{lang}/admin/... на /admin/... чтобы избежать 404."""
    target = f"/admin/{rest_path}"
    return RedirectResponse(url=target, status_code=302)

@app.get("/{lang}/static/{path:path}")
async def static_with_lang(lang: str, path: str):
    # Редиректим на правильный путь статики без обработки сессии
    from starlette.responses import RedirectResponse
    return RedirectResponse(url=f"/static/{path}", status_code=307)
