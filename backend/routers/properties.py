from fastapi import APIRouter, Request, HTTPException, Depends, Query, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session, joinedload
from backend.database import get_db
from backend.models.property import Property
from backend.models.property_image import PropertyImage
from pathlib import Path
from backend.config.templates import templates
from backend.routers.user_tools import notify_telegram
from datetime import datetime
# Используем современную систему переводов через middleware
from backend.fix_i18n_modern import inject_translator_to_templates

import os

router = APIRouter()

# 🔍 Фильтр (карточки)
@router.get("/filter", response_class=HTMLResponse)
async def filter_properties(
    request: Request,
    query: str = Query(default="", alias="query"),
    property_type: str = "",
    bedrooms: int = 0,
    price_from: float = 0,
    price_to: float = 0,
    page: int = 1,
    db: Session = Depends(get_db),
):
    filters = []

    if query:
        filters.append(Property.district.ilike(f"%{query}%"))
    if property_type:
        filters.append(Property.property_type == property_type)
    if bedrooms:
        filters.append(Property.bedrooms >= bedrooms)
    if price_from:
        filters.append(Property.price >= price_from)
    if price_to:
        filters.append(Property.price <= price_to)

    page_size = 8
    offset = (page - 1) * page_size

    properties = db.query(Property)\
        .options(joinedload(Property.images))\
        .filter(*filters)\
        .offset(offset)\
        .limit(page_size + 1)\
        .all()

    next_page = page + 1 if len(properties) > page_size else None
    properties = properties[:page_size]

    return templates.TemplateResponse("components/property_cards.html", {
        "request": request,
        "properties": properties,
        "next_page": next_page
    })


# 🏠 Главная страница списка объектов
@router.get("/", response_class=HTMLResponse)
def list_properties(
    request: Request,
    query: str = "",
    property_type: str = "",
    bedrooms: int = 0,
    price_from: int = 0,
    price_to: int = 999999999,
    district: str = "",
    deal_type: str = "",
    available_now: bool = False,
    pets_allowed: bool = False,
    private_pool: bool = False,
    balcony: bool = False,
    sea_view: bool = False,
    parking: bool = False,
    gym: bool = False,
    wifi: bool = False,
    washing_machine: bool = False,
    db: Session = Depends(get_db)
):
    # Принудительная инжекция переводчика (страховка)
    inject_translator_to_templates(templates, request)
    filters = []

    if query:
        filters.append(
            Property.title.ilike(f"%{query}%") | 
            Property.description.ilike(f"%{query}%") |
            Property.district.ilike(f"%{query}%")
        )
    if property_type:
        filters.append(Property.property_type == property_type)
    if bedrooms:
        filters.append(Property.bedrooms >= bedrooms)
    if price_from and price_from > 0:
        filters.append(Property.price >= price_from)
    if price_to and price_to < 999999999:
        filters.append(Property.price <= price_to)
    if district:
        filters.append(Property.district.ilike(f"%{district}%"))
    
    # Фильтрация по типу сделки
    if deal_type == "buy":
        # Для продажи исключаем объекты с периодичной арендой
        filters.append(Property.price_period.is_(None) | Property.price_period.in_(["", "total"]))
    elif deal_type == "rent":
        # Для аренды показываем только с периодами аренды
        filters.append(Property.price_period.in_(["month", "day", "week", "year"]))
    
    if available_now:
        filters.append(Property.status == "available")
    if pets_allowed:
        filters.append(Property.pets_allowed == True)

    properties = db.query(Property)\
        .options(joinedload(Property.images))\
        .filter(*filters)\
        .order_by(Property.id.desc())\
        .all()
    
    # Получаем уникальные районы для фильтра
    districts = db.query(Property.district)\
        .filter(Property.district.isnot(None))\
        .distinct()\
        .all()
    districts = [d[0] for d in districts if d[0]]
    
    # Выбираем шаблон в зависимости от типа сделки
    template_name = "properties_catalog.html" if deal_type == "buy" else "rent.html"
    
    return templates.TemplateResponse(template_name, {
        "request": request,
        "properties": properties, 
        "districts": districts,
        "selected_query": query,
        "selected_property_type": property_type,
        "selected_bedrooms": bedrooms,
        "selected_price_from": price_from if price_from > 0 else "",
        "selected_price_to": price_to if price_to < 999999999 else "",
        "selected_district": district,
        "deal_type": deal_type
    })


# 🏗️ Каталог новостроек
@router.get("/new-builds", response_class=HTMLResponse)
def new_builds_catalog(
    request: Request,
    property_type: str = "",  # "apartment" или "villa"
    district: str = "",
    db: Session = Depends(get_db)
):
    # Принудительная инжекция переводчика (страховка)
    inject_translator_to_templates(templates, request)
    
    filters = [Property.is_new_building == True]
    
    if property_type:
        filters.append(Property.property_type == property_type)
    if district:
        filters.append(Property.district == district)
    
    properties = db.query(Property)\
        .options(joinedload(Property.images))\
        .filter(*filters)\
        .all()
    
    # Получаем уникальные районы для фильтра
    districts = db.query(Property.district)\
        .filter(Property.is_new_building == True, Property.district.isnot(None))\
        .distinct()\
        .all()
    districts = [d[0] for d in districts if d[0]]
    
    return templates.TemplateResponse("new_builds_catalog.html", {
        "request": request,
        "properties": properties,
        "districts": districts,
        "selected_type": property_type,
        "selected_district": district
    })


# 🔍 AJAX фильтр для новостроек
@router.get("/new-builds/filter", response_class=HTMLResponse)
async def filter_new_builds(
    request: Request,
    property_type: str = Query(default=""),
    district: str = Query(default=""),
    db: Session = Depends(get_db),
):
    filters = [Property.is_new_building == True]
    
    if property_type:
        filters.append(Property.property_type == property_type)
    if district:
        filters.append(Property.district == district)

    properties = db.query(Property)\
        .options(joinedload(Property.images))\
        .filter(*filters)\
        .all()

    return templates.TemplateResponse("components/new_builds_cards.html", {
        "request": request,
        "properties": properties
    })


# 📄 Страница аренды с фильтрацией
@router.get("/rent", response_class=HTMLResponse)
def rent_page(
    request: Request,
    query: str = "",
    bedrooms: int = 0,
    price_from: float = 0,
    price_to: float = 0,
    district: bool = False,
    available_now: bool = False,
    pets_allowed: bool = False,
    private_pool: bool = False,
    balcony: bool = False,
    sea_view: bool = False,
    parking: bool = False,
    gym: bool = False,
    wifi: bool = False,
    washing_machine: bool = False,
    db: Session = Depends(get_db)
):
    # Принудительная инжекция переводчика (страховка)
    inject_translator_to_templates(templates, request)
    
    filters = [Property.property_type == "rent"]

    if query:
        filters.append(Property.title.ilike(f"%{query}%"))
    if bedrooms:
        filters.append(Property.bedrooms >= bedrooms)
    if price_from:
        filters.append(Property.price >= price_from)
    if price_to:
        filters.append(Property.price <= price_to)
    if district:
        filters.append(Property.district != None)
    if available_now:
        filters.append(Property.available == True)
    if pets_allowed:
        filters.append(Property.pets_allowed == True)
    if private_pool:
        filters.append(Property.private_pool == True)
    if balcony:
        filters.append(Property.balcony == True)
    if sea_view:
        filters.append(Property.sea_view == True)
    if parking:
        filters.append(Property.parking == True)
    if gym:
        filters.append(Property.gym == True)
    if wifi:
        filters.append(Property.wifi == True)
    if washing_machine:
        filters.append(Property.washing_machine == True)

    properties = db.query(Property).filter(*filters).all()

    return templates.TemplateResponse("rent.html", {
        "request": request,
        "properties": properties,
        "next_page": 2
    })


# 🔍 Детальная страница объекта
@router.get("/{id}", response_class=HTMLResponse)
def property_detail(request: Request, id: int, lang: str, db: Session = Depends(get_db)):
    # Принудительная инжекция переводчика (страховка)
    inject_translator_to_templates(templates, request)
    
    property = db.query(Property).filter(Property.id == id).first()
    if not property:
        return HTMLResponse(content="Property not found", status_code=404)

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



