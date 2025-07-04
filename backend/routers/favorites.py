from fastapi import APIRouter, Request, Response, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session, joinedload
from backend.database import SessionLocal
from backend.models.favorite import Favorite
from backend.models.property import Property
from backend.config.templates import templates
# Используем современную систему переводов через ModernI18nMiddleware
import uuid

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_or_create_session_id(request: Request, response: Response):
    """Получить или создать session_id для анонимного пользователя"""
    session_id = request.cookies.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie('session_id', session_id, max_age=30*24*60*60)  # 30 дней
    return session_id

# 📍 Страница избранного
@router.get("/favorites", response_class=HTMLResponse)
async def favorites_page(
    request: Request, 
    response: Response,
    db: Session = Depends(get_db)
):
    session_id = get_or_create_session_id(request, response)
    
    # Получаем избранные объекты с информацией о недвижимости
    favorites = db.query(Favorite)\
        .options(joinedload(Favorite.property).joinedload(Property.images))\
        .filter(Favorite.session_id == session_id)\
        .order_by(Favorite.created_at.desc())\
        .all()
    
    # Переводчик доступен автоматически через ModernI18nMiddleware
    return templates.TemplateResponse("favorites.html", {
        "request": request,
        "favorites": favorites,
        "total_count": len(favorites)
    })

# ➕ Добавить в избранное
@router.post("/favorites/add/{property_id}")
async def add_to_favorites(
    property_id: int,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    session_id = get_or_create_session_id(request, response)
    
    # Проверяем, существует ли недвижимость
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Объект недвижимости не найден")
    
    # Проверяем, не добавлено ли уже в избранное
    existing_favorite = db.query(Favorite)\
        .filter(Favorite.session_id == session_id, Favorite.property_id == property_id)\
        .first()
    
    if existing_favorite:
        return JSONResponse({
            "success": False,
            "message": "Уже добавлено в избранное",
            "in_favorites": True
        })
    
    # Добавляем в избранное
    new_favorite = Favorite(
        session_id=session_id,
        property_id=property_id
    )
    db.add(new_favorite)
    db.commit()
    
    # Подсчитываем общее количество избранных
    total_count = db.query(Favorite).filter(Favorite.session_id == session_id).count()
    
    return JSONResponse({
        "success": True,
        "message": "Добавлено в избранное",
        "in_favorites": True,
        "total_count": total_count
    })

# ➖ Удалить из избранного
@router.delete("/favorites/remove/{property_id}")
async def remove_from_favorites(
    property_id: int,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    session_id = get_or_create_session_id(request, response)
    
    # Находим и удаляем из избранного
    favorite = db.query(Favorite)\
        .filter(Favorite.session_id == session_id, Favorite.property_id == property_id)\
        .first()
    
    if not favorite:
        return JSONResponse({
            "success": False,
            "message": "Не найдено в избранном",
            "in_favorites": False
        })
    
    db.delete(favorite)
    db.commit()
    
    # Подсчитываем общее количество избранных
    total_count = db.query(Favorite).filter(Favorite.session_id == session_id).count()
    
    return JSONResponse({
        "success": True,
        "message": "Удалено из избранного",
        "in_favorites": False,
        "total_count": total_count
    })

# 🔍 Проверить статус избранного
@router.get("/favorites/check/{property_id}")
async def check_favorite_status(
    property_id: int,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    session_id = get_or_create_session_id(request, response)
    
    favorite = db.query(Favorite)\
        .filter(Favorite.session_id == session_id, Favorite.property_id == property_id)\
        .first()
    
    total_count = db.query(Favorite).filter(Favorite.session_id == session_id).count()
    
    return JSONResponse({
        "in_favorites": favorite is not None,
        "total_count": total_count
    })

# 🔄 Переключить избранное (toggle)
@router.post("/favorites/toggle/{property_id}")
async def toggle_favorite(
    property_id: int,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    session_id = get_or_create_session_id(request, response)
    
    # Проверяем, существует ли недвижимость
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Объект недвижимости не найден")
    
    # Проверяем, есть ли уже в избранном
    existing_favorite = db.query(Favorite)\
        .filter(Favorite.session_id == session_id, Favorite.property_id == property_id)\
        .first()
    
    if existing_favorite:
        # Удаляем из избранного
        db.delete(existing_favorite)
        db.commit()
        favorited = False
        message = "Удалено из избранного"
    else:
        # Добавляем в избранное
        new_favorite = Favorite(
            session_id=session_id,
            property_id=property_id
        )
        db.add(new_favorite)
        db.commit()
        favorited = True
        message = "Добавлено в избранное"
    
    # Подсчитываем общее количество избранных
    total_count = db.query(Favorite).filter(Favorite.session_id == session_id).count()
    
    return JSONResponse({
        "success": True,
        "message": message,
        "favorited": favorited,
        "total_count": total_count
    })

# 📋 Получить список избранного (JSON)
@router.get("/favorites/list")
async def get_favorites_list(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    session_id = get_or_create_session_id(request, response)
    
    favorites = db.query(Favorite)\
        .filter(Favorite.session_id == session_id)\
        .all()
    
    return JSONResponse({
        "favorites": [{"property_id": fav.property_id} for fav in favorites],
        "total_count": len(favorites)
    })

# 🔍 Проверить статус нескольких объектов
@router.post("/favorites/check-multiple")
async def check_multiple_favorite_status(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    session_id = get_or_create_session_id(request, response)
    
    try:
        body = await request.json()
        property_ids = body.get('property_ids', [])
    except:
        property_ids = []
    
    if not property_ids:
        return JSONResponse({"favorites": {}, "total_count": 0})
    
    favorites = db.query(Favorite)\
        .filter(
            Favorite.session_id == session_id,
            Favorite.property_id.in_(property_ids)
        )\
        .all()
    
    favorite_dict = {fav.property_id: True for fav in favorites}
    result = {prop_id: favorite_dict.get(prop_id, False) for prop_id in property_ids}
    
    total_count = db.query(Favorite).filter(Favorite.session_id == session_id).count()
    
    return JSONResponse({
        "favorites": result,
        "total_count": total_count
    })

# 🗑️ Очистить избранное
@router.delete("/favorites/clear")
async def clear_favorites(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    session_id = get_or_create_session_id(request, response)
    
    # Удаляем все избранные объекты пользователя
    db.query(Favorite).filter(Favorite.session_id == session_id).delete()
    db.commit()
    
    return JSONResponse({
        "success": True,
        "message": "Избранное очищено",
        "total_count": 0
    }) 