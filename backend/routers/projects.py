from fastapi import APIRouter, Depends, Request, Query, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from pathlib import Path
from datetime import datetime
import json
from backend.config.templates import templates
from backend.database import get_db, SessionLocal
from backend.models.property import Property
from backend.models.project import Project
from backend.fix_i18n_modern import inject_translator_to_templates

# 📁 Базовая директория и шаблоны
BASE_DIR = Path(__file__).resolve().parent.parent

# Функция для принудительного декодирования текста
def safe_decode(text):
    if not text:
        return text
    if isinstance(text, bytes):
        return text.decode('utf-8', errors='ignore')
    if isinstance(text, str):
        # Попробуем исправить кодировку
        try:
            # Если это строка с неправильной кодировкой, перекодируем
            return text.encode('latin1').decode('utf-8', errors='ignore')
        except:
            return text
    return text

def safe_decode_array(arr):
    """Безопасно декодирует массив строк (или одну строку). Если приходит строка,
    превращает её в список, разделяя по запятой."""
    if not arr:
        return []

    # Если сохранено как строка "one, two, three" – превращаем в список
    if isinstance(arr, str):
        arr = [a.strip() for a in arr.split(',') if a.strip()]

    return [safe_decode(item) for item in arr]

router = APIRouter()

# 📦 Подключение БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Каталог проектов
@router.get("/projects", response_class=HTMLResponse)
async def projects_catalog(
    request: Request, 
    lang: str,
    status: str = Query(default=""),
    district: str = Query(default=""),
    db: Session = Depends(get_db)
):
    # Принудительная инжекция переводчика (страховка)
    inject_translator_to_templates(templates, request)
    
    try:
        filters = []
        
        if status:
            filters.append(Project.status == status)
        if district:
            filters.append(Project.district == district)
        
        projects_raw = db.query(Project).filter(*filters).all()
        print(f"Found {len(projects_raw)} projects")  # Отладка
        
        # Очищаем данные всех проектов
        projects = []
        for p in projects_raw:
            clean_p = type('obj', (object,), {
                'id': p.id,
                'slug': p.slug,
                'title': p.title,
                'subtitle': safe_decode(p.subtitle),
                'description': safe_decode(p.description),
                'district': safe_decode(p.district),
                'developer': p.developer,
                'completion_year': p.completion_year,
                'price_from': p.price_from,
                'price_to': p.price_to,
                'hero_image': p.hero_image,
                'highlights': safe_decode_array(p.highlights),
                'status': p.status,
                'is_featured': p.is_featured
            })
            projects.append(clean_p)
        
    except Exception as e:
        print(f"Error loading projects: {e}")
        projects = []  # Возвращаем пустой список при ошибке
    
    # Получаем уникальные районы для фильтра
    districts = db.query(Project.district)\
        .filter(Project.district.isnot(None))\
        .distinct()\
        .all()
    districts = [d[0] for d in districts if d[0]]
    
    return templates.TemplateResponse("projects_catalog.html", {
        "request": request,
        "projects": projects,
        "districts": districts,
        "selected_status": status,
        "selected_district": district
    })

# ✅ Детальная страница проекта по slug
@router.get("/projects/{project_slug}", response_class=HTMLResponse)
async def project_detail(
    request: Request, 
    lang: str,
    project_slug: str, 
    db: Session = Depends(get_db)
):
    # Принудительная инжекция переводчика (страховка)
    inject_translator_to_templates(templates, request)
    
    try:
        print(f"Looking for project with slug: {project_slug}")  # Отладка
        project = db.query(Project).filter(Project.slug == project_slug).first()
        
        if not project:
            print(f"Project not found: {project_slug}")  # Отладка
            raise HTTPException(status_code=404, detail="Проект не найден")
        
        print(f"Found project: {project.title}")  # Отладка
        
        # Создаем очищенную версию данных проекта
        clean_project = type('obj', (object,), {
            'id': project.id,
            'slug': project.slug,
            'title': project.title,
            'subtitle': safe_decode(project.subtitle),
            'description': safe_decode(project.description),
            'location': project.location,
            'district': safe_decode(project.district),
            'developer': project.developer,
            'completion_year': project.completion_year,
            'total_units': project.total_units,
            'floors': project.floors,
            'price_from': project.price_from,
            'price_to': project.price_to,
            'currency': project.currency,
            'hero_image': project.hero_image,
            'gallery_images': project.gallery_images,
            'highlights': safe_decode_array(project.highlights),
            'amenities': safe_decode_array(project.amenities),
            'unit_types': project.unit_types,
            'payment_plan': safe_decode(project.payment_plan),
            'down_payment': project.down_payment,
            'monthly_payment': project.monthly_payment,
            'roi_info': project.roi_info,
            'status': project.status,
            'is_featured': project.is_featured
        })
        
        # Отладка (комментируем из-за ошибок линтера)
        # print(f"Description after decode: {clean_project.description}")
        # print(f"Highlights after decode: {clean_project.highlights}")
        
    except Exception as e:
        print(f"Error loading project: {e}")
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    # Получаем связанные объекты недвижимости из этого проекта (по району или названию)
    related_properties = db.query(Property)\
        .filter(
            Property.district == project.district,
            Property.is_new_building == True
        )\
        .limit(6)\
        .all()
    
    # Другие проекты в том же районе
    related_projects = db.query(Project)\
        .filter(
            Project.district == project.district,
            Project.id != project.id,
            Project.status == "active"
        )\
        .limit(3)\
        .all()
    
    return templates.TemplateResponse("project_detail.html", {
        "request": request,
        "project": clean_project,
        "related_properties": related_properties,
        "related_projects": related_projects
    })

# ✅ API для получения проектов (для AJAX)
@router.get("/api/projects")
def get_projects_api(
    request: Request,
    lang: str,
    status: str = Query(default=""),
    district: str = Query(default=""),
    featured_only: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    filters = []

    if status:
        filters.append(Project.status == status)
    if district:
        filters.append(Project.district == district)
    if featured_only:
        filters.append(Project.is_featured == True)

    projects = db.query(Project).filter(*filters).all()
    
    return {
        "projects": [
            {
                "id": p.id,
                "slug": p.slug,
                "title": p.title,
                "subtitle": p.subtitle,
                "location": p.location,
                "district": p.district,
                "developer": p.developer,
                "price_from": p.price_from,
                "price_to": p.price_to,
                "hero_image": p.hero_image,
                "highlights": p.highlights,
                "completion_year": p.completion_year
            }
            for p in projects
        ]
    }

# Устаревшие роуты - для обратной совместимости
@router.get("/projects/pty-residence", response_class=HTMLResponse)
async def pty_redirect(request: Request, lang: str):
    return templates.TemplateResponse(
        "redirect.html", 
        {"request": request, "redirect_url": f"/{lang}/projects/pty-residence"}
    )

@router.get("/projects/zenith-pattaya", response_class=HTMLResponse)
async def zenith_redirect(request: Request, lang: str):
    return templates.TemplateResponse(
        "redirect.html", 
        {"request": request, "redirect_url": f"/{lang}/projects/zenith-pattaya"}
    )

# Устаревший роут аренды - перенесен в properties.py
@router.get("/rent", response_class=HTMLResponse)
async def rent_page_redirect(request: Request, lang: str):
    return templates.TemplateResponse(
        "redirect.html", 
        {"request": request, "redirect_url": f"/{lang}/properties?deal_type=rent"}
    )

# 🧪 Тестовый роут для проверки работы роутера
@router.get("/projects/test", response_class=HTMLResponse)
async def test_projects_router(request: Request, lang: str):
    return HTMLResponse(content=f"""
    <h1>✅ Projects Router Working!</h1>
    <p>Language: {lang}</p>
    <p>Time: {datetime.now()}</p>
    <p><a href="/{lang}/projects">Back to projects catalog</a></p>
    """)
