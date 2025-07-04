from fastapi import APIRouter, Request, Form, UploadFile, File, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from sqlalchemy.orm import Session
from backend.database import get_db, SessionLocal
from backend.models.property import Property
from backend.models.property_image import PropertyImage
from backend.models.project import Project
from pathlib import Path
from typing import List
import tempfile

# Условные импорты для дополнительных функций
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

import shutil
import uuid
import os
from datetime import datetime, date
# Используем современную систему переводов через ModernI18nMiddleware
from backend.config.templates import templates

router = APIRouter()


# ✅ Панель администратора
@router.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request, db: Session = Depends(get_db)):
    properties = db.query(Property).all()
    projects = db.query(Project).all()
    return templates.TemplateResponse("admin.html", {
        "request": request, 
        "properties": properties, 
        "projects": projects
    })


# ✅ Форма добавления объекта
@router.get("/admin/add", response_class=HTMLResponse)
def add_property_form(request: Request):
    return templates.TemplateResponse("add_property.html", {"request": request})


# ✅ Обработка добавления объекта
@router.post("/admin/add", response_class=HTMLResponse)
async def add_property_submit(
    request: Request,
    title: str = Form(...),
    condo_name: str = Form(""),
    district: str = Form(""),
    location: str = Form(""),
    property_type: str = Form(""),
    status: str = Form("available"),
    price: float = Form(...),
    price_period: str = Form("month"),
    old_price: float = Form(None),
    bedrooms: int = Form(0),
    bathrooms: int = Form(0),
    area: float = Form(0),
    land_area: float = Form(None),
    floor: str = Form(""),
    furnished: str = Form(""),
    published_at: str = Form(""),
    lat: str = Form(""),
    lng: str = Form(""),
    features: List[str] = Form(default=[]),
    images: List[UploadFile] = File([]),
    description: str = Form(""),
    is_new_building: bool = Form(False)
):
    db = SessionLocal()
    try:
        new_property = Property(
            title=title,
            condo_name=condo_name,
            district=district,
            location=location,
            property_type=property_type,
            status=status,
            price=price,
            price_period=price_period,
            old_price=old_price,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            area=area,
            land_area=land_area,
            floor=floor,
            furnished=furnished,
            published_at=published_at.strip() if published_at else None,
            lat=float(lat) if lat else None,
            lng=float(lng) if lng else None,
            description=description,
            features=features if features else [],
            is_new_building=is_new_building
        )

        db.add(new_property)
        db.commit()
        db.refresh(new_property)

        os.makedirs("static/uploads", exist_ok=True)

        for image in images:
            if image.filename:
                filename = f"{uuid.uuid4().hex}_{image.filename}"
                file_path = f"static/uploads/{filename}"
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)

                db_image = PropertyImage(
                    property_id=new_property.id,
                    image_url=f"/{file_path}"
                )
                db.add(db_image)

        db.commit()
        return templates.TemplateResponse("add_property.html", {
            "request": request,
            "success": True
        })

    except Exception as e:
        db.rollback()
        return templates.TemplateResponse("add_property.html", {
            "request": request,
            "error": f"Ошибка при сохранении: {e}"
        })
    finally:
        db.close()


# ✅ Удаление объекта
@router.get("/admin/delete/{property_id}", response_class=HTMLResponse)
def delete_property(property_id: int, db: Session = Depends(get_db)):
    try:
        prop = db.query(Property).get(property_id)
        if not prop:
            raise HTTPException(status_code=404, detail="Property not found")

        for img in prop.images:
            file_path = Path("backend") / img.image_url.lstrip("/")
            if file_path.exists():
                file_path.unlink()

        db.delete(prop)
        db.commit()
        return RedirectResponse(url="/admin", status_code=303)
    except Exception as e:
        db.rollback()
        return HTMLResponse(f"<h1>Ошибка при удалении: {e}</h1>", status_code=500)


# ✅ Удаление отдельного изображения
@router.get("/admin/delete-image/{image_id}", response_class=RedirectResponse)
def delete_image(image_id: int, db: Session = Depends(get_db)):
    image = db.query(PropertyImage).get(image_id)
    if image:
        file_path = Path("backend") / image.image_url.lstrip("/")
        if file_path.exists():
            file_path.unlink()

        db.delete(image)
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)


# ✅ Управление объектами
@router.get("/admin/properties", response_class=HTMLResponse)
def admin_properties(request: Request, db: Session = Depends(get_db)):
    properties = db.query(Property).all()
    return templates.TemplateResponse("property_list_admin.html", {"request": request, "properties": properties})


# 🏠 УПРАВЛЕНИЕ АРЕНДОЙ - Основная страница
@router.get("/admin/rental", response_class=HTMLResponse)
def admin_rental_page(request: Request, db: Session = Depends(get_db)):
    """Основная страница управления арендой"""
    try:
        # Загружаем все объекты недвижимости для аренды
        properties = db.query(Property).filter(
            Property.price_period.in_(["month", "day", "week"])
        ).all()
        
        # Статистика по аренде
        stats = {
            "total": len(properties),
            "available": len([p for p in properties if getattr(p, 'rental_status', 'available') == 'available']),
            "rented": len([p for p in properties if getattr(p, 'rental_status', 'available') == 'rented']),
            "maintenance": len([p for p in properties if getattr(p, 'rental_status', 'available') == 'maintenance'])
        }
        
        return templates.TemplateResponse("rental_admin.html", {
            "request": request,
            "properties": properties,
            "stats": stats
        })
    except Exception as e:
        print(f"Ошибка загрузки страницы аренды: {e}")
        return templates.TemplateResponse("rental_admin.html", {
            "request": request,
            "properties": [],
            "stats": {"total": 0, "available": 0, "rented": 0, "maintenance": 0}
        })


# 🏗️ РОУТЕРЫ ДЛЯ ПРОЕКТОВ

# ✅ Форма добавления проекта
@router.get("/admin/add-project", response_class=HTMLResponse)
def add_project_form(request: Request):
    return templates.TemplateResponse("add_project.html", {"request": request})


# ✅ Обработка добавления проекта
@router.post("/admin/add-project", response_class=HTMLResponse)
async def add_project_submit(
    request: Request,
    title: str = Form(...),
    slug: str = Form(...),
    subtitle: str = Form(""),
    description: str = Form(""),
    location: str = Form(""),
    district: str = Form(""),
    developer: str = Form(""),
    completion_year: int = Form(None),
    total_units: int = Form(None),
    floors: int = Form(None),
    status: str = Form("active"),
    price_from: float = Form(None),
    price_to: float = Form(None),
    lat: str = Form(""),
    lng: str = Form(""),
    down_payment: str = Form(""),
    monthly_payment: str = Form(""),
    sales_office_phone: str = Form(""),
    sales_office_email: str = Form(""),
    sales_office_address: str = Form(""),
    highlights: str = Form(""),
    amenities: List[str] = Form(default=[]),
    payment_plan: str = Form(""),
    roi_info: str = Form(""),
    unit_types: str = Form(""),
    is_featured: bool = Form(False),
    hero_image: UploadFile = File(None),
    gallery_images: List[UploadFile] = File([]),
    video_url: str = Form(""),
    meta_title: str = Form(""),
    meta_description: str = Form("")
):
    db = SessionLocal()
    try:
        # Проверяем уникальность slug
        existing_project = db.query(Project).filter(Project.slug == slug).first()
        if existing_project:
            return templates.TemplateResponse("add_project.html", {
                "request": request,
                "error": f"Новостройка с slug '{slug}' уже существует. Выберите другой slug."
            })

        # Создаем объект проекта
        new_project = Project(
            title=title,
            slug=slug,
            subtitle=subtitle or None,
            description=description or None,
            location=location or None,
            district=district or None,
            developer=developer or None,
            completion_year=completion_year,
            total_units=total_units,
            floors=floors,
            status=status,
            price_from=price_from,
            price_to=price_to,
            lat=float(lat) if lat else None,
            lng=float(lng) if lng else None,
            down_payment=down_payment or None,
            monthly_payment=monthly_payment or None,
            sales_office_phone=sales_office_phone or None,
            sales_office_email=sales_office_email or None,
            sales_office_address=sales_office_address or None,
            highlights=[h.strip() for h in highlights.split(',') if h.strip()] if highlights else None,
            amenities=amenities if amenities else None,
            payment_plan=payment_plan or None,
            roi_info=roi_info or None,
            unit_types=unit_types or None,
            is_featured=is_featured,
            video_url=video_url or None,
            meta_title=meta_title or None,
            meta_description=meta_description or None
        )

        # Сохраняем проект в БД
        db.add(new_project)
        db.commit()
        db.refresh(new_project)

        # Создаем папку для загрузок если её нет
        os.makedirs("static/uploads", exist_ok=True)

        # Обрабатываем главное изображение
        hero_image_path = None
        if hero_image and hero_image.filename:
            filename = f"{uuid.uuid4().hex}_{hero_image.filename}"
            file_path = f"static/uploads/{filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(hero_image.file, buffer)
            hero_image_path = f"/{file_path}"

        # Обрабатываем галерею изображений
        gallery_paths = []
        for image in gallery_images:
            if image.filename:
                filename = f"{uuid.uuid4().hex}_{image.filename}"
                file_path = f"static/uploads/{filename}"
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                gallery_paths.append(f"/{file_path}")

        # Обновляем проект с изображениями
        if hero_image_path or gallery_paths:
            if hero_image_path:
                db.query(Project).filter(Project.id == new_project.id).update({"hero_image": hero_image_path})
            if gallery_paths:
                db.query(Project).filter(Project.id == new_project.id).update({"gallery_images": gallery_paths})

        # Сохраняем изменения
        db.commit()

        return templates.TemplateResponse("add_project.html", {
            "request": request,
            "success": True
        })

    except Exception as e:
        db.rollback()
        return templates.TemplateResponse("add_project.html", {
            "request": request,
            "error": f"Ошибка при сохранении: {e}"
        })
    finally:
        db.close()


# ✅ Список проектов для администратора
@router.get("/admin/projects", response_class=HTMLResponse)
def admin_projects(request: Request, db: Session = Depends(get_db)):
    projects = db.query(Project).all()

    return templates.TemplateResponse("project_list_admin.html", {"request": request, "projects": projects})


# ✅ Удаление проекта
@router.get("/admin/delete-project/{project_id}", response_class=HTMLResponse)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    try:
        project = db.query(Project).get(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Удаляем файлы изображений
        if project.hero_image:
            file_path = Path("backend") / project.hero_image.lstrip("/")
            if file_path.exists():
                file_path.unlink()

        if project.gallery_images:
            for img_path in project.gallery_images:
                file_path = Path("backend") / img_path.lstrip("/")
                if file_path.exists():
                    file_path.unlink()

        db.delete(project)
        db.commit()
        return RedirectResponse(url="/admin/projects", status_code=303)
    except Exception as e:
        db.rollback()
        return HTMLResponse(f"<h1>Ошибка при удалении: {e}</h1>", status_code=500)


# ✅ Форма редактирования проекта
@router.get("/admin/projects/edit/{project_id}", response_class=HTMLResponse)
def edit_project_form(request: Request, project_id: int, db: Session = Depends(get_db)):
    import json
    project = db.query(Project).get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Преобразуем в dict для JS-скрипта шаблона
    project_dict = {
        "title": project.title,
        "slug": project.slug,
        "subtitle": project.subtitle,
        "developer": project.developer,
        "district": project.district,
        "location": project.location,
        "lat": project.lat,
        "lng": project.lng,
        "completion_year": project.completion_year,
        "total_units": project.total_units,
        "floors": project.floors,
        "status": project.status,
        "price_from": project.price_from,
        "price_to": project.price_to,
        "description": project.description,
        "highlights": project.highlights,
        "amenities": project.amenities or []
    }

    return templates.TemplateResponse(
        "add_project.html",
        {
            "request": request,
            "project": project,
            "edit_mode": True,
            "project_json": json.dumps(project_dict, ensure_ascii=False)
        }
    )


# ✅ Обработка сохранения изменений проекта
@router.post("/admin/projects/edit/{project_id}", response_class=HTMLResponse)
async def update_project_submit(
    project_id: int,
    request: Request,
    title: str = Form(...),
    slug: str = Form(...),
    subtitle: str = Form(""),
    description: str = Form(""),
    location: str = Form(""),
    district: str = Form(""),
    developer: str = Form(""),
    completion_year: int = Form(None),
    total_units: int = Form(None),
    floors: int = Form(None),
    status: str = Form("active"),
    price_from: float = Form(None),
    price_to: float = Form(None),
    lat: str = Form(""),
    lng: str = Form(""),
    highlights: str = Form(""),
    amenities: List[str] = Form(default=[]),
    payment_plan: str = Form(""),
    roi_info: str = Form(""),
    unit_types: str = Form(""),
    db: Session = Depends(get_db)
):
    try:
        project = db.query(Project).get(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Обновляем поля
        project.title = title
        project.slug = slug
        project.subtitle = subtitle
        project.description = description
        project.location = location
        project.district = district
        project.developer = developer
        project.completion_year = completion_year
        project.total_units = total_units
        project.floors = floors
        project.status = status
        project.price_from = price_from
        project.price_to = price_to
        project.lat = float(lat) if lat else None
        project.lng = float(lng) if lng else None
        project.highlights = [h.strip() for h in highlights.split(',') if h.strip()]
        project.amenities = amenities if amenities else []
        project.payment_plan = payment_plan
        project.roi_info = roi_info
        project.unit_types = unit_types

        db.commit()

        return RedirectResponse(url="/admin/projects", status_code=303)
    except Exception as e:
        db.rollback()
        return HTMLResponse(f"<h1>Ошибка при сохранении: {e}</h1>", status_code=500)

# 📊 Получение статистики по аренде
@router.get("/admin/rental/stats")
def rental_stats(db: Session = Depends(get_db)):
    from datetime import datetime, timedelta
    
    try:
        total_properties = db.query(Property).count()
        available_properties = db.query(Property).filter(Property.rental_status == "available").count()
        rented_properties = db.query(Property).filter(Property.rental_status == "rented").count()
        maintenance_properties = db.query(Property).filter(Property.rental_status == "maintenance").count()
        
        # Находим объекты с истекающими договорами аренды (в ближайшие 30 дней)
        expiring_soon = db.query(Property).filter(
            Property.rental_status == "rented",
            Property.rental_end_date != None,
            Property.rental_end_date <= datetime.now() + timedelta(days=30)
        ).count()
        
        return {
            "total": total_properties,
            "available": available_properties,
            "rented": rented_properties,
            "maintenance": maintenance_properties,
            "expiring_soon": expiring_soon
        }
        
    except Exception as e:
        return {"error": str(e)}

# ========== РАСШИРЕННЫЕ ФУНКЦИИ АДМИНКИ ==========

# 👥 УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ
@router.get("/admin/users", response_class=HTMLResponse)
def admin_users(request: Request, db: Session = Depends(get_db)):
    from backend.models.user import User
    from datetime import datetime
    
    try:
        # Получаем всех пользователей с сортировкой по дате создания
        users = db.query(User).order_by(User.created_at.desc()).all()
    except Exception as e:
        print(f"Ошибка загрузки пользователей: {e}")
        # Возвращаем пустой список если есть проблемы с БД
        users = []
    
    # Статистика по пользователям
    total_users = len(users)
    active_users = len([u for u in users if u.is_active == True])
    new_users_today = len([u for u in users if u.created_at and u.created_at.date() == datetime.utcnow().date()])
    
    stats = {
        'total': total_users,
        'active': active_users,
        'new_today': new_users_today,
        'whatsapp': len([u for u in users if u.whatsapp_number is not None and u.whatsapp_number != ""]),
        'telegram': len([u for u in users if u.telegram_id is not None and u.telegram_id != ""]),
        'instagram': len([u for u in users if u.instagram_id is not None and u.instagram_id != ""])
    }
    

    return templates.TemplateResponse("admin/users.html", {
        "request": request, 
        "users": users,
        "stats": stats,
        "_": _
    })

# 📊 АНАЛИТИКА И СТАТИСТИКА  
@router.get("/admin/analytics", response_class=HTMLResponse)
def admin_analytics(request: Request, db: Session = Depends(get_db)):
    # Базовая статистика
    properties_count = db.query(Property).count()
    projects_count = db.query(Project).count()
    available_count = db.query(Property).filter(Property.status == 'available').count()
    
    # TODO: Добавить более детальную аналитику
    stats = {
        'properties_total': properties_count,
        'projects_total': projects_count,
        'available_total': available_count,
        'views_total': 1234,  # Заглушка
        'leads_total': 56,    # Заглушка
        'conversion_rate': 4.5 # Заглушка
    }
    

    return templates.TemplateResponse("admin/analytics.html", {
        "request": request, 
        "stats": stats,
        "_": _
    })

# 📝 УПРАВЛЕНИЕ КОНТЕНТОМ - перенаправляем на статьи
@router.get("/admin/content")
def admin_content(request: Request, db: Session = Depends(get_db)):
    """Центральное управление контентом"""
    import os
    from pathlib import Path
    

    
    # Статистика контента
    try:
        # Статьи
        articles_dir = Path("backend/articles/markdown")
        articles_count = len(list(articles_dir.glob("*.md"))) if articles_dir.exists() else 0
        
        # Изображения
        images_dir = Path("static/uploads")
        images_count = len(list(images_dir.glob("*.*"))) if images_dir.exists() else 0
        
        # Статистика БД
        stats = {
            "articles_count": articles_count,
            "images_count": images_count,
            "properties_count": db.query(Property).count(),
            "projects_count": db.query(Project).count(),
            "published_properties": db.query(Property).filter(Property.status == 'available').count(),
            "published_projects": db.query(Project).filter(Project.status == 'active').count()
        }
        
        # Размер папок
        def get_dir_size(path):
            if not Path(path).exists():
                return 0
            total = 0
            for file_path in Path(path).rglob('*'):
                if file_path.is_file():
                    total += file_path.stat().st_size
            return total / 1024 / 1024  # MB
        
        stats["images_size_mb"] = f"{get_dir_size('static/uploads'):.1f}"
        stats["articles_size_mb"] = f"{get_dir_size('backend/articles'):.1f}"
        
    except Exception as e:
        stats = {"error": str(e)}
    
    # Последние изменения
    recent_changes = []
    try:
        # Последние добавленные объекты
        recent_properties = db.query(Property).order_by(Property.id.desc()).limit(5).all()
        for prop in recent_properties:
            recent_changes.append({
                "type": "property",
                "title": prop.title,
                "date": "недавно",  # В реальности взять created_at
                "status": prop.status,
                "url": f"/admin/properties"
            })
    except:
        pass
    
    return templates.TemplateResponse("admin/content.html", {
        "request": request,
        "stats": stats,
        "recent_changes": recent_changes,
        "_": _
    })

@router.post("/admin/content/cleanup")
def cleanup_content(request: Request):
    """Очистка неиспользуемого контента"""
    from pathlib import Path
    import os
    
    try:
        removed_files = []
        
        # Находим изображения без привязки к объектам
        uploads_dir = Path("static/uploads")
        if uploads_dir.exists():
            for image_file in uploads_dir.glob("*.*"):
                # Здесь можно добавить логику проверки использования файла
                # Пока что заглушка
                pass
        
        return {"success": True, "message": f"Очистка завершена. Удалено: {len(removed_files)} файлов"}
        
    except Exception as e:
        return {"success": False, "message": f"Ошибка очистки: {str(e)}"}

@router.get("/admin/content/media")
def content_media(request: Request):
    """Управление медиафайлами"""
    from pathlib import Path
    import os
    

    
    # Получаем список всех изображений
    media_files = []
    uploads_dir = Path("static/uploads")
    
    if uploads_dir.exists():
        for file_path in uploads_dir.glob("*.*"):
            if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                stat = file_path.stat()
                media_files.append({
                    "filename": file_path.name,
                    "size": f"{stat.st_size / 1024:.1f} KB",
                    "modified": stat.st_mtime,
                    "url": f"/static/uploads/{file_path.name}"
                })
    
    # Сортируем по дате изменения (новые сначала)
    media_files.sort(key=lambda x: x["modified"], reverse=True)
    
    return templates.TemplateResponse("admin/media.html", {
        "request": request,
        "media_files": media_files[:50],  # Показываем только последние 50
        "total_files": len(media_files),
        "_": _
    })

@router.post("/admin/content/media/delete/{filename}")
def delete_media_file(filename: str):
    """Удаление медиафайла"""
    from pathlib import Path
    
    try:
        file_path = Path("static/uploads") / filename
        
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
            return {"success": True, "message": "Файл удален"}
        else:
            return {"success": False, "message": "Файл не найден"}
            
    except Exception as e:
        return {"success": False, "message": f"Ошибка удаления: {str(e)}"}

# 🔧 СИСТЕМНЫЕ НАСТРОЙКИ
@router.get("/admin/settings", response_class=HTMLResponse)
def admin_settings(request: Request):

    return templates.TemplateResponse("admin/settings.html", {
        "request": request,
        "_": _
    })

# 📋 ЛОГИ СИСТЕМЫ
@router.get("/admin/logs", response_class=HTMLResponse)
def admin_logs(request: Request):
    # TODO: Реализовать чтение логов
    logs = []  # Заглушка

    return templates.TemplateResponse("admin/logs.html", {
        "request": request,
        "logs": logs,
        "_": _
    })

# 💾 РЕЗЕРВНОЕ КОПИРОВАНИЕ
@router.get("/admin/backup", response_class=HTMLResponse)
def admin_backup(request: Request, db: Session = Depends(get_db)):
    """Страница управления бэкапами"""
    import subprocess
    from pathlib import Path
    

    
    # Получаем информацию о бэкапах
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    backups = []
    if backup_dir.exists():
        for backup_file in backup_dir.glob("*.sql"):
            stat = backup_file.stat()
            backups.append({
                "filename": backup_file.name,
                "size": f"{stat.st_size / 1024 / 1024:.1f} MB",
                "created": datetime.fromtimestamp(stat.st_mtime).strftime("%d.%m.%Y %H:%M"),
                "path": str(backup_file)
            })
    
    # Статистика базы данных
    try:
        # Количество записей в основных таблицах
        from backend.models.user import User
        stats = {
            "users_count": db.query(User).count(),
            "properties_count": db.query(Property).count(), 
            "projects_count": db.query(Project).count(),
        }
        
        # Размер диска (с обработкой отсутствия psutil)
        try:
            import psutil
            disk_usage = psutil.disk_usage('.')
            stats["disk_free"] = f"{disk_usage.free / 1024 / 1024 / 1024:.1f} GB"
            stats["disk_total"] = f"{disk_usage.total / 1024 / 1024 / 1024:.1f} GB"
        except ImportError:
            # Если psutil не установлен
            stats["disk_free"] = "N/A (установите psutil)"
            stats["disk_total"] = "N/A (установите psutil)"
        
    except Exception as e:
        stats = {"error": str(e)}
    
    return templates.TemplateResponse("admin/backup.html", {
        "request": request,
        "backups": sorted(backups, key=lambda x: x["created"], reverse=True),
        "stats": stats,
        "_": _
    })

@router.post("/admin/backup/create")
def create_backup(request: Request, db: Session = Depends(get_db)):
    """Создание бэкапа базы данных"""
    import subprocess
    from pathlib import Path
    
    try:
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Генерируем имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"thailand_realty_backup_{timestamp}.sql"
        backup_path = backup_dir / backup_filename
        
        # Команда для создания бэкапа PostgreSQL
        cmd = [
            "pg_dump",
            "-h", "localhost",
            "-U", "postgres", 
            "-d", "thailand_realty",
            "-f", str(backup_path),
            "--no-password"
        ]
        
        # Выполняем команду
        result = subprocess.run(cmd, capture_output=True, text=True, env={
            "PGPASSWORD": "your_password"  # В продакшене использовать переменные окружения
        })
        
        if result.returncode == 0:
            return {"success": True, "message": f"Бэкап создан: {backup_filename}"}
        else:
            return {"success": False, "message": f"Ошибка создания бэкапа: {result.stderr}"}
            
    except Exception as e:
        return {"success": False, "message": f"Ошибка: {str(e)}"}

@router.get("/admin/backup/download/{filename}")
def download_backup(filename: str):
    """Скачивание файла бэкапа"""
    backup_path = Path("backups") / filename
    
    if not backup_path.exists():
        raise HTTPException(status_code=404, detail="Файл бэкапа не найден")
    
    return FileResponse(
        path=str(backup_path),
        filename=filename,
        media_type="application/sql"
    )

@router.post("/admin/backup/delete/{filename}")
def delete_backup(filename: str):
    """Удаление файла бэкапа"""
    backup_path = Path("backups") / filename
    
    try:
        if backup_path.exists():
            backup_path.unlink()
            return {"success": True, "message": "Бэкап удален"}
        else:
            return {"success": False, "message": "Файл не найден"}
    except Exception as e:
        return {"success": False, "message": f"Ошибка удаления: {str(e)}"}

# 📞 ЗАЯВКИ КЛИЕНТОВ
@router.get("/admin/requests", response_class=HTMLResponse)
def admin_requests(request: Request, db: Session = Depends(get_db)):
    # TODO: Добавить модель для заявок клиентов
    requests = []  # Заглушка

    return templates.TemplateResponse("admin/requests.html", {
        "request": request,
                 "requests": requests,
         "_": _
     })

# 📊 ЭКСПОРТ ПОЛЬЗОВАТЕЛЕЙ В EXCEL
@router.get("/admin/users/export")
def export_users_excel(db: Session = Depends(get_db)):
    """Экспорт всех пользователей в Excel или CSV файл"""
    from backend.models.user import User
    import csv
    
    # Получаем всех пользователей
    users = db.query(User).order_by(User.created_at.desc()).all()
    
    # Подготавливаем данные для экспорта
    data = []
    headers = ['ID', 'Имя', 'Email', 'Телефон', 'WhatsApp', 'Telegram', 'Instagram', 
               'Город', 'Страна', 'Бюджет от', 'Бюджет до', 'Тип недвижимости', 
               'Источник', 'Статус', 'Приоритет', 'Заметки', 'Дата создания', 
               'Последний контакт', 'Активен']
    
    for user in users:
        data.append([
            user.id,
            user.full_name or '',
            user.email or '',
            user.phone or '',
            user.whatsapp_number or '',
            user.telegram_id or '',
            user.instagram_id or '',
            user.city or '',
            user.country or '',
            user.budget_min or '',
            user.budget_max or '',
            user.property_type or '',
            user.source or '',
            user.status or '',
            user.priority or '',
            user.notes or '',
            user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else '',
            user.last_contact.strftime('%Y-%m-%d %H:%M:%S') if user.last_contact else '',
            'Да' if user.is_active else 'Нет'
        ])
    
    try:
        # Если pandas доступен, создаем Excel файл
        if PANDAS_AVAILABLE:
            import pandas as pd
            import openpyxl
            
            # Создаем DataFrame из списков
            df = pd.DataFrame(data, columns=headers)
            
            # Создаем временный файл Excel
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                with pd.ExcelWriter(tmp_file.name, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Пользователи', index=False)
                    
                    # Автоматическая ширина колонок
                    worksheet = writer.sheets['Пользователи']
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
                
                filename = f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                return FileResponse(
                    path=tmp_file.name,
                    filename=filename,
                    media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
        
        # Fallback на CSV файл
        else:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w', encoding='utf-8-sig', newline='') as tmp_file:
                writer = csv.writer(tmp_file)
                writer.writerow(headers)  # Заголовки
                writer.writerows(data)    # Данные
                
                filename = f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                return FileResponse(
                    path=tmp_file.name,
                    filename=filename,
                    media_type='text/csv'
                )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка экспорта: {str(e)}")

# 👤 ДОБАВЛЕНИЕ НОВОГО ПОЛЬЗОВАТЕЛЯ
@router.post("/admin/users/add")
async def add_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(""),
    phone: str = Form(""),
    whatsapp: str = Form(""),
    telegram: str = Form(""),
    instagram: str = Form(""),
    city: str = Form(""),
    country: str = Form(""),
    budget_min: str = Form(""),
    budget_max: str = Form(""),
    property_type: str = Form(""),
    source: str = Form(""),
    notes: str = Form(""),
    priority: str = Form("medium"),
    db: Session = Depends(get_db)
):
    """Добавление нового пользователя"""
    from backend.models.user import User
    
    try:
        # Преобразуем budget в числа, если указаны
        budget_min_int = None
        budget_max_int = None
        
        if budget_min and budget_min.strip():
            try:
                budget_min_int = int(budget_min)
            except ValueError:
                pass
                
        if budget_max and budget_max.strip():
            try:
                budget_max_int = int(budget_max)
            except ValueError:
                pass
        
        new_user = User(
            full_name=name,
            email=email if email else None,
            phone=phone if phone else None,
            whatsapp_number=whatsapp if whatsapp else None,
            telegram_id=telegram if telegram else None,
            instagram_id=instagram if instagram else None,
            city=city if city else None,
            country=country if country else None,
            budget_min=budget_min_int,
            budget_max=budget_max_int,
            property_type=property_type if property_type else None,
            source=source if source else None,
            notes=notes if notes else None,
            priority=priority,
            status="new",
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        
        return RedirectResponse(url="/admin/users", status_code=303)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении пользователя: {str(e)}")

# 🎯 SEO УПРАВЛЕНИЕ
@router.get("/admin/seo", response_class=HTMLResponse)
def admin_seo(request: Request, db: Session = Depends(get_db)):
    """Управление SEO настройками"""
    import json
    from pathlib import Path
    

    
    # Загружаем настройки SEO из файла
    seo_file = Path("backend/seo_settings.json")
    seo_settings = {}
    
    if seo_file.exists():
        try:
            with open(seo_file, 'r', encoding='utf-8') as f:
                seo_settings = json.load(f)
        except:
            pass
    
    # Значения по умолчанию
    default_settings = {
        "site_title": "Sianoro Real Estate - Недвижимость в Таиланде",
        "site_description": "Покупка и аренда недвижимости в Паттайе, Таиланд. Квартиры, виллы, новостройки от проверенных застройщиков.",
        "site_keywords": "недвижимость таиланд, паттайя, квартиры, виллы, покупка, аренда",
        "robots_txt": "User-agent: *\nDisallow: /admin/\nAllow: /\n\nSitemap: https://sianoro.com/sitemap.xml",
        "google_analytics": "",
        "yandex_metrica": "",
        "facebook_pixel": "",
        "google_search_console": "",
        "canonical_domain": "https://sianoro.com",
        "social_title": "Sianoro Real Estate",
        "social_description": "Недвижимость в Таиланде от экспертов",
        "social_image": "/static/img/sianoro-logo.png"
    }
    
    # Объединяем с настройками по умолчанию
    for key, value in default_settings.items():
        if key not in seo_settings:
            seo_settings[key] = value
    
    # Статистика SEO
    try:
        stats = {
            "properties_with_meta": db.query(Property).filter(Property.title != None).count(),
            "properties_total": db.query(Property).count(),
            "projects_with_meta": db.query(Project).filter(Project.meta_title != None).count(), 
            "projects_total": db.query(Project).count(),
        }
    except Exception as e:
        stats = {"error": str(e)}
    
    return templates.TemplateResponse("admin/seo.html", {
        "request": request,
        "seo_settings": seo_settings,
        "stats": stats,
        "_": _
    })

@router.post("/admin/seo/save")
def save_seo_settings(
    request: Request,
    site_title: str = Form(...),
    site_description: str = Form(...),
    site_keywords: str = Form(...),
    robots_txt: str = Form(...),
    google_analytics: str = Form(""),
    yandex_metrica: str = Form(""), 
    facebook_pixel: str = Form(""),
    google_search_console: str = Form(""),
    canonical_domain: str = Form(""),
    social_title: str = Form(""),
    social_description: str = Form(""),
    social_image: str = Form("")
):
    """Сохранение SEO настроек"""
    import json
    from pathlib import Path
    
    try:
        seo_settings = {
            "site_title": site_title,
            "site_description": site_description,
            "site_keywords": site_keywords,
            "robots_txt": robots_txt,
            "google_analytics": google_analytics,
            "yandex_metrica": yandex_metrica,
            "facebook_pixel": facebook_pixel,
            "google_search_console": google_search_console,
            "canonical_domain": canonical_domain,
            "social_title": social_title,
            "social_description": social_description,
            "social_image": social_image
        }
        
        # Сохраняем в файл
        seo_file = Path("backend/seo_settings.json")
        with open(seo_file, 'w', encoding='utf-8') as f:
            json.dump(seo_settings, f, ensure_ascii=False, indent=2)
        
        # Обновляем robots.txt
        robots_file = Path("static/robots.txt")
        with open(robots_file, 'w', encoding='utf-8') as f:
            f.write(robots_txt)
        
        return {"success": True, "message": "SEO настройки сохранены"}
        
    except Exception as e:
        return {"success": False, "message": f"Ошибка сохранения: {str(e)}"}

@router.get("/admin/seo/generate-sitemap")
def generate_sitemap(db: Session = Depends(get_db)):
    """Генерация sitemap.xml"""
    from datetime import datetime
    import xml.etree.ElementTree as ET
    from pathlib import Path
    
    try:
        # Создаем корневой элемент
        urlset = ET.Element("urlset")
        urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
        
        base_url = "https://sianoro.com"  # В продакшене брать из настроек
        
        # Главные страницы
        main_pages = [
            {"url": f"{base_url}/ru", "priority": "1.0"},
            {"url": f"{base_url}/en", "priority": "1.0"},
            {"url": f"{base_url}/ru/properties", "priority": "0.8"},
            {"url": f"{base_url}/ru/projects", "priority": "0.8"},
            {"url": f"{base_url}/ru/properties/rent", "priority": "0.8"},
            {"url": f"{base_url}/ru/articles", "priority": "0.7"},
        ]
        
        for page in main_pages:
            url_elem = ET.SubElement(urlset, "url")
            ET.SubElement(url_elem, "loc").text = page["url"]
            ET.SubElement(url_elem, "lastmod").text = datetime.now().strftime("%Y-%m-%d")
            ET.SubElement(url_elem, "priority").text = page["priority"]
        
        # Добавляем объекты недвижимости
        properties = db.query(Property).filter(Property.status == 'available').all()
        for prop in properties:
            url_elem = ET.SubElement(urlset, "url")
            ET.SubElement(url_elem, "loc").text = f"{base_url}/ru/property/{prop.id}"
            ET.SubElement(url_elem, "lastmod").text = datetime.now().strftime("%Y-%m-%d")
            ET.SubElement(url_elem, "priority").text = "0.6"
        
        # Добавляем проекты
        projects = db.query(Project).filter(Project.status == 'active').all()
        for project in projects:
            url_elem = ET.SubElement(urlset, "url")
            ET.SubElement(url_elem, "loc").text = f"{base_url}/ru/project/{project.slug}"
            ET.SubElement(url_elem, "lastmod").text = datetime.now().strftime("%Y-%m-%d")
            ET.SubElement(url_elem, "priority").text = "0.7"
        
        # Сохраняем в файл
        tree = ET.ElementTree(urlset)
        sitemap_file = Path("static/sitemap.xml")
        tree.write(sitemap_file, encoding="utf-8", xml_declaration=True)
        
        return {"success": True, "message": f"Sitemap создан с {len(list(urlset))} URL"}
        
    except Exception as e:
        return {"success": False, "message": f"Ошибка создания sitemap: {str(e)}"}

# 📱 МОБИЛЬНОЕ ПРИЛОЖЕНИЕ (заготовка)
@router.get("/admin/mobile", response_class=HTMLResponse)
def admin_mobile(request: Request):

    return templates.TemplateResponse("admin/mobile.html", {
        "request": request,
        "_": _
    })

# 🔔 УВЕДОМЛЕНИЯ
@router.get("/admin/notifications", response_class=HTMLResponse)
def admin_notifications(request: Request):
    # TODO: Система уведомлений
    notifications = []  # Заглушка

    return templates.TemplateResponse("admin/notifications.html", {
        "request": request,
        "notifications": notifications,
        "_": _
    })

# ⚡ API ДЛЯ AJAX-ЗАПРОСОВ

@router.get("/admin/api/stats")
def api_stats(db: Session = Depends(get_db)):
    """API для получения статистики в реальном времени"""
    return {
        "properties": db.query(Property).count(),
        "projects": db.query(Project).count(),
        "available": db.query(Property).filter(Property.status == 'available').count(),
        "visitors": 1234,  # Заглушка
        "timestamp": "now"
    }

@router.get("/admin/api/recent-activity")
def api_recent_activity(db: Session = Depends(get_db)):
    """API для получения последних действий"""
    # TODO: Реализовать логгирование действий админа
    return [
        {
            "action": "Добавлен новый объект недвижимости",
            "time": "2 часа назад",
            "type": "property"
        },
        {
            "action": "Обновлен проект 'Zenith Tower'", 
            "time": "5 часов назад",
            "type": "project"
        },
        {
            "action": "Новая заявка от клиента",
            "time": "1 день назад", 
            "type": "request"
        }
    ]

# 📚 УПРАВЛЕНИЕ СТАТЬЯМИ

@router.get("/admin/articles", response_class=HTMLResponse)
def admin_articles(request: Request):
    """Управление статьями"""
    try:
        # Загружаем статьи из markdown файлов
        articles = load_articles_for_admin()
        total_articles = len(articles)
        
    
        return templates.TemplateResponse("admin/articles.html", {
            "request": request,
            "articles": articles,
            "total_articles": total_articles,
            "_": _
        })
    except Exception as e:
        print(f"Ошибка загрузки статей: {e}")
        return templates.TemplateResponse("admin/articles.html", {
            "request": request,
            "articles": [],
            "total_articles": 0,
            
        })

@router.get("/admin/articles/add", response_class=HTMLResponse)
def admin_add_article(request: Request):
    """Форма добавления статьи"""

    return templates.TemplateResponse("admin/add_article.html", {
        "request": request,
        "_": _
    })

@router.post("/admin/articles/add")
async def admin_create_article(
    request: Request,
    title: str = Form(...),
    slug: str = Form(...),
    excerpt: str = Form(""),
    content: str = Form(...),
    category: str = Form("tips"),
    published: bool = Form(False),
    featured_image: UploadFile = File(None)
):
    """Создание новой статьи"""
    try:
        from pathlib import Path
        import frontmatter
        from datetime import datetime
        import shutil
        import uuid
        
        # Создаем markdown файл
        articles_dir = Path(__file__).resolve().parent.parent / "articles" / "markdown"
        articles_dir.mkdir(parents=True, exist_ok=True)
        
        # Создаем папку для изображений статей
        images_dir = Path("static/images/articles")
        images_dir.mkdir(parents=True, exist_ok=True)
        
        # Обрабатываем загрузку изображения
        featured_image_path = None
        if featured_image and featured_image.filename:
            # Проверяем размер файла (2MB максимум)
            content = await featured_image.read()
            if len(content) > 2 * 1024 * 1024:
                return templates.TemplateResponse("admin/add_article.html", {
                    "request": request,
                    "error": "Размер изображения не должен превышать 2MB",
                    "title": title,
                    "slug": slug,
                    "excerpt": excerpt,
                    "content": content,
                    
                })
            
            # Проверяем тип файла
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if featured_image.content_type not in allowed_types:
                return templates.TemplateResponse("admin/add_article.html", {
                    "request": request,
                    "error": "Поддерживаются только форматы: JPG, PNG, WebP",
                    "title": title,
                    "slug": slug,
                    "excerpt": excerpt,
                    "content": content,
                    
                })
            
            # Генерируем уникальное имя файла
            file_extension = featured_image.filename.split('.')[-1].lower()
            unique_filename = f"{slug}_{uuid.uuid4().hex[:8]}.{file_extension}"
            image_path = images_dir / unique_filename
            
            # Сохраняем файл
            with open(image_path, 'wb') as f:
                f.write(content)
            
            # Сохраняем относительный путь для использования в шаблонах
            featured_image_path = f"/static/images/articles/{unique_filename}"
        
        # Подготавливаем метаданные
        metadata = {
            'title': title,
            'slug': slug,
            'excerpt': excerpt,
            'category': category,
            'published': published,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Добавляем путь к изображению, если есть
        if featured_image_path:
            metadata['featured_image'] = featured_image_path
        
        # Создаем объект frontmatter
        post = frontmatter.Post(content, **metadata)
        
        # Сохраняем файл
        file_path = articles_dir / f"{slug}.md"
        
        if file_path.exists():
            return templates.TemplateResponse("admin/add_article.html", {
                "request": request,
                "error": "Статья с таким slug уже существует",
                "title": title,
                "slug": slug,
                "excerpt": excerpt,
                "content": content,
                
            })
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        return RedirectResponse(url="/admin/articles", status_code=302)
    
    except Exception as e:
        print(f"Ошибка создания статьи: {e}")
        return templates.TemplateResponse("admin/add_article.html", {
            "request": request,
            "error": f"Ошибка создания статьи: {str(e)}",
            "title": title,
            "slug": slug,
            "excerpt": excerpt,
            "content": content,
            
        })

@router.get("/admin/articles/edit/{slug}", response_class=HTMLResponse)
def admin_edit_article(request: Request, slug: str):
    """Страница редактирования статьи"""
    try:
        from pathlib import Path
        import frontmatter
        
        articles_dir = Path(__file__).resolve().parent.parent / "articles" / "markdown"
        file_path = articles_dir / f"{slug}.md"
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Статья не найдена")
        
        # Загружаем статью
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
        except UnicodeDecodeError:
            # Пробуем другие кодировки
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                post = frontmatter.load(f)
        
        article_data = {
            "slug": post.get("slug", slug),
            "title": post.get("title", ""),
            "excerpt": post.get("excerpt", ""),
            "content": post.content,
            "category": post.get("category", "tips"),
            "published": post.get("published", False),
            "featured_image": post.get("featured_image", ""),
            "created_at": post.get("created_at", ""),
            "updated_at": post.get("updated_at", "")
        }
        
    
        return templates.TemplateResponse("admin/edit_article.html", {
            "request": request,
            "article": article_data,
            "_": _
        })
        
    except Exception as e:
        print(f"Ошибка загрузки статьи: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки статьи: {str(e)}")

@router.post("/admin/articles/edit/{slug}")
async def admin_update_article(
    request: Request,
    slug: str,
    title: str = Form(...),
    excerpt: str = Form(""),
    content: str = Form(...),
    category: str = Form("tips"),
    published: bool = Form(False),
    featured_image: UploadFile = File(None),
    remove_image: bool = Form(False)
):
    """Обновление статьи"""
    try:
        from pathlib import Path
        import frontmatter
        from datetime import datetime
        import uuid
        
        articles_dir = Path(__file__).resolve().parent.parent / "articles" / "markdown"
        file_path = articles_dir / f"{slug}.md"
        
        if not file_path.exists():
            return templates.TemplateResponse("admin/edit_article.html", {
                "request": request,
                "error": "Статья не найдена",
                "article": {"slug": slug, "title": title, "excerpt": excerpt, "content": content},
                
            })
        
        # Загружаем существующую статью
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
        except UnicodeDecodeError:
            # Пробуем другие кодировки
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                post = frontmatter.load(f)
        
        # Обрабатываем изображение
        featured_image_path = post.get("featured_image", "")
        
        # Удаление изображения
        if remove_image:
            if featured_image_path and featured_image_path.startswith("/static/images/articles/"):
                try:
                    old_image_path = Path("static") / featured_image_path[8:]  # убираем "/static/"
                    if old_image_path.exists():
                        old_image_path.unlink()
                except Exception as e:
                    print(f"Ошибка удаления изображения: {e}")
            featured_image_path = ""
        
        # Загрузка нового изображения
        if featured_image and featured_image.filename:
            # Проверка размера (2MB максимум)
            image_content = await featured_image.read()
            if len(image_content) > 2 * 1024 * 1024:
                return templates.TemplateResponse("admin/edit_article.html", {
                    "request": request,
                    "error": "Размер изображения не должен превышать 2MB",
                    "article": {"slug": slug, "title": title, "excerpt": excerpt, "content": content},
                    
                })
            
            # Проверка типа файла
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if featured_image.content_type not in allowed_types:
                return templates.TemplateResponse("admin/edit_article.html", {
                    "request": request,
                    "error": "Поддерживаются только форматы: JPG, PNG, WebP",
                    "article": {"slug": slug, "title": title, "excerpt": excerpt, "content": content},
                    
                })
            
            # Удаляем старое изображение
            if featured_image_path and featured_image_path.startswith("/static/images/articles/"):
                try:
                    old_image_path = Path("static") / featured_image_path[8:]
                    if old_image_path.exists():
                        old_image_path.unlink()
                except Exception as e:
                    print(f"Ошибка удаления старого изображения: {e}")
            
            # Сохраняем новое изображение
            images_dir = Path("static/images/articles")
            images_dir.mkdir(parents=True, exist_ok=True)
            
            file_extension = featured_image.filename.split('.')[-1].lower()
            unique_filename = f"{slug}_{uuid.uuid4().hex[:8]}.{file_extension}"
            image_path = images_dir / unique_filename
            
            with open(image_path, 'wb') as f:
                f.write(image_content)
            
            featured_image_path = f"/static/images/articles/{unique_filename}"
        
        # Подготавливаем обновленные метаданные
        metadata = {
            'title': title,
            'slug': slug,
            'excerpt': excerpt,
            'category': category,
            'published': published,
            'created_at': post.get('created_at', datetime.now().isoformat()),
            'updated_at': datetime.now().isoformat()
        }
        
        # Добавляем путь к изображению, если есть
        if featured_image_path:
            metadata['featured_image'] = featured_image_path
        
        # Создаем обновленный объект frontmatter
        updated_post = frontmatter.Post(content, **metadata)
        
        # Сохраняем файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(updated_post))
        
        return RedirectResponse(url="/admin/articles", status_code=302)
    
    except Exception as e:
        print(f"Ошибка обновления статьи: {e}")
        return templates.TemplateResponse("admin/edit_article.html", {
            "request": request,
            "error": f"Ошибка обновления статьи: {str(e)}",
            "article": {"slug": slug, "title": title, "excerpt": excerpt, "content": content},
            
        })

@router.post("/admin/articles/publish/{slug}")
def admin_publish_article(slug: str):
    """Публикация/снятие с публикации статьи"""
    try:
        from pathlib import Path
        import frontmatter
        from datetime import datetime
        
        articles_dir = Path(__file__).resolve().parent.parent / "articles" / "markdown"
        file_path = articles_dir / f"{slug}.md"
        
        if not file_path.exists():
            return JSONResponse({"success": False, "message": "Статья не найдена"})
        
        # Загружаем статью
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
        except UnicodeDecodeError:
            # Пробуем другие кодировки
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                post = frontmatter.load(f)
        
        # Переключаем статус публикации
        current_status = post.get("published", False)
        new_status = not current_status
        
        # Обновляем метаданные
        post.metadata['published'] = new_status
        post.metadata['updated_at'] = datetime.now().isoformat()
        
        # Сохраняем файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(post))
        
        action = "опубликована" if new_status else "снята с публикации"
        return JSONResponse({"success": True, "message": f"Статья {action}", "published": new_status})
    
    except Exception as e:
        print(f"Ошибка изменения статуса публикации: {e}")
        return JSONResponse({"success": False, "message": f"Ошибка: {str(e)}"})

@router.post("/admin/articles/delete/{slug}")
def admin_delete_article(slug: str):
    """Удаление статьи"""
    try:
        from pathlib import Path
        
        articles_dir = Path(__file__).resolve().parent.parent / "articles" / "markdown"
        file_path = articles_dir / f"{slug}.md"
        
        if file_path.exists():
            file_path.unlink()
            return JSONResponse({"success": True, "message": "Статья удалена"})
        else:
            return JSONResponse({"success": False, "message": "Статья не найдена"})
    
    except Exception as e:
        print(f"Ошибка удаления статьи: {e}")
        return JSONResponse({"success": False, "message": f"Ошибка: {str(e)}"})

# Вспомогательные функции для работы со статьями

def load_articles_for_admin():
    """Загрузка статей для админки с дополнительными метаданными"""
    from pathlib import Path
    import frontmatter
    
    articles_dir = Path(__file__).resolve().parent.parent / "articles" / "markdown"
    if not articles_dir.exists():
        return []
    
    articles = []
    for file_path in articles_dir.glob("*.md"):
        try:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
            except UnicodeDecodeError:
                # Пробуем другие кодировки
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    post = frontmatter.load(f)
            
            articles.append({
                "slug": post.get("slug", file_path.stem),
                "title": post.get("title", file_path.stem),
                "excerpt": post.get("excerpt", ""),
                "category": post.get("category", "tips"),
                "published": post.get("published", True),
                "created_at": post.get("created_at", ""),
                "updated_at": post.get("updated_at", ""),
                "file_size": file_path.stat().st_size,
                "content": post.content
            })
        except Exception as e:
            print(f"Ошибка загрузки файла {file_path}: {e}")
            continue
    
    return sorted(articles, key=lambda x: x.get("updated_at", ""), reverse=True)

@router.get("/rental")
async def rental_admin(request: Request):
    """Страница управления арендой недвижимости"""
    try:
        db = next(get_db())
        
        # Загружаем объекты для аренды
        rental_properties = db.query(Property).filter(
            Property.deal_type == "rent"
        ).all()
        
        return templates.TemplateResponse(
            "rental_admin.html",
            {
                "request": request,
                "rental_properties": rental_properties
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "rental_admin.html",
            {
                "request": request,
                "rental_properties": [],
                "error": f"Ошибка загрузки данных: {str(e)}"
            }
        )

@router.post("/update-property/{property_id}")
async def update_property(
    property_id: int,
    request: Request,
    title: str = Form(None),
    price: int = Form(None),
    property_type: str = Form(None),
    status: str = Form(None),
    is_new_building: bool = Form(False)
):
    """API для обновления основных свойств недвижимости (продажа)"""
    try:
        db = next(get_db())
        property_obj = db.query(Property).filter(Property.id == property_id).first()
        
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Обновляем только переданные поля
        if title is not None:
            property_obj.title = title
        if price is not None:
            property_obj.price = price
        if property_type is not None:
            property_obj.property_type = property_type
        if status is not None:
            property_obj.status = status
        if is_new_building is not None:
            property_obj.is_new_building = is_new_building
        
        db.commit()
        
        return {"success": True, "message": "Property updated successfully"}
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )

@router.get("/edit-property/{property_id}")
async def edit_property_detail(property_id: int, request: Request):
    """Детальное редактирование объекта недвижимости"""
    try:
        db = next(get_db())
        property_obj = db.query(Property).filter(Property.id == property_id).first()
        
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        
        return templates.TemplateResponse(
            "edit_property_detail.html",
            {"request": request, "property": property_obj}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/add-rental")
async def add_rental_form(request: Request):
    """Форма добавления объекта аренды"""
    return templates.TemplateResponse(
        "add_rental_property.html",
        {"request": request}
    )

@router.post("/add-rental")
async def create_rental_property(
    request: Request,
    title: str = Form(...),
    property_type: str = Form(...),
    district: str = Form(...),
    price: int = Form(...),
    price_period: str = Form("month"),
    currency: str = Form("THB"),
    bedrooms: int = Form(0),
    area: int = Form(None),
    short_description: str = Form(...),
    description: str = Form(""),
    contact_phone: str = Form(""),
    whatsapp: str = Form(""),
    amenities: list = Form([]),
    images: list[UploadFile] = File([])
):
    """Создание нового объекта аренды"""
    try:
        db = next(get_db())
        
        # Создаем объект недвижимости для аренды
        new_property = Property(
            title=title,
            property_type=property_type,
            district=district,
            price=price,
            price_period=price_period,
            currency=currency,
            bedrooms=bedrooms,
            area=area,
            short_description=short_description,
            description=description,
            contact_phone=contact_phone,
            whatsapp=whatsapp,
            amenities=",".join(amenities) if amenities else "",
            deal_type="rent",  # Помечаем как аренду
            status="available",
            rental_status="available"  # Устанавливаем статус аренды
        )
        
        db.add(new_property)
        db.flush()  # Получаем ID
        
        # Сохраняем изображения
        if images and images[0].filename:
            import os
            import uuid
            from backend.models.property_image import PropertyImage
            
            upload_dir = "static/uploads"
            os.makedirs(upload_dir, exist_ok=True)
            
            for image in images:
                if image.filename:
                    # Генерируем уникальное имя файла
                    file_ext = os.path.splitext(image.filename)[1]
                    filename = f"{uuid.uuid4()}{file_ext}"
                    file_path = os.path.join(upload_dir, filename)
                    
                    # Сохраняем файл
                    with open(file_path, "wb") as f:
                        content = await image.read()
                        f.write(content)
                    
                    # Создаем запись в БД
                    property_image = PropertyImage(
                        property_id=new_property.id,
                        image_url=f"/static/uploads/{filename}",
                        alt_text=f"Фото {title}"
                    )
                    db.add(property_image)
        
        db.commit()
        
        return RedirectResponse(url="/admin/rental?success=1", status_code=303)
        
    except Exception as e:
        db.rollback()
        return templates.TemplateResponse(
            "add_rental_property.html",
            {
                "request": request,
                "error": f"Ошибка при создании объекта: {str(e)}"
            }
        )

# ✏️ РЕДАКТИРОВАНИЕ ПОЛЬЗОВАТЕЛЯ  
@router.get("/admin/users/edit/{user_id}", response_class=HTMLResponse)
def edit_user_form(user_id: int, request: Request, db: Session = Depends(get_db)):
    """Форма редактирования пользователя"""
    from backend.models.user import User
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
    
        return templates.TemplateResponse("admin/edit_user.html", {
            "request": request,
            "user": user,
            "_": _
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки пользователя: {str(e)}")

@router.post("/admin/users/edit/{user_id}")
async def update_user(
    user_id: int,
    request: Request,
    name: str = Form(...),
    email: str = Form(""),
    phone: str = Form(""),
    whatsapp: str = Form(""),
    telegram: str = Form(""),
    instagram: str = Form(""),
    city: str = Form(""),
    country: str = Form(""),
    budget_min: str = Form(""),
    budget_max: str = Form(""),
    property_type: str = Form(""),
    source: str = Form(""),
    notes: str = Form(""),
    priority: str = Form("medium"),
    status: str = Form("new"),
    is_active: bool = Form(True),
    db: Session = Depends(get_db)
):
    """Обновление данных пользователя"""
    from backend.models.user import User
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Преобразуем budget в числа, если указаны
        budget_min_int = None
        budget_max_int = None
        
        if budget_min and budget_min.strip():
            try:
                budget_min_int = int(budget_min)
            except ValueError:
                pass
                
        if budget_max and budget_max.strip():
            try:
                budget_max_int = int(budget_max)
            except ValueError:
                pass
        
        # Обновляем данные пользователя
        user.full_name = name
        user.email = email if email else None
        user.phone = phone if phone else None
        user.whatsapp_number = whatsapp if whatsapp else None
        user.telegram_id = telegram if telegram else None
        user.instagram_id = instagram if instagram else None
        user.city = city if city else None
        user.country = country if country else None
        user.budget_min = budget_min_int
        user.budget_max = budget_max_int
        user.property_type = property_type if property_type else None
        user.source = source if source else None
        user.notes = notes if notes else None
        user.priority = priority
        user.status = status
        user.is_active = is_active
        
        db.commit()
        
        return RedirectResponse(url="/admin/users", status_code=303)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка обновления пользователя: {str(e)}")

# 🗑️ УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ
@router.post("/admin/users/delete/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Удаление пользователя"""
    from backend.models.user import User
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        db.delete(user)
        db.commit()
        
        return RedirectResponse(url="/admin/users", status_code=303)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка удаления пользователя: {str(e)}")

# 📞 ОТМЕТИТЬ КОНТАКТ С ПОЛЬЗОВАТЕЛЕМ
@router.post("/admin/users/contact/{user_id}")
def mark_contact(user_id: int, db: Session = Depends(get_db)):
    """Отметить контакт с пользователем"""
    from backend.models.user import User
    from datetime import datetime
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Обновляем время последнего контакта и статус
        user.last_contact = datetime.utcnow()
        if user.status == 'new':
            user.status = 'contacted'
        
        db.commit()
        
        return RedirectResponse(url="/admin/users", status_code=303)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка отметки контакта: {str(e)}")
