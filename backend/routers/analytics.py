from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta
from backend.database import get_db
from backend.models.user import User
from backend.models.property import Property
from backend.models.project import Project
from backend.config.templates import templates
from typing import Dict, Any
import calendar

router = APIRouter()

@router.get("/admin/analytics")
async def analytics_dashboard(request: Request, db: Session = Depends(get_db)):
    """Расширенная аналитическая панель"""
    try:
        # 📊 Основная статистика
        total_users = db.query(User).count()
        total_properties = db.query(Property).count()
        total_projects = db.query(Project).count()
        
        # 📅 Статистика за последние 30 дней
        thirty_days_ago = datetime.now() - timedelta(days=30)
        new_users_month = db.query(User).filter(User.created_at >= thirty_days_ago).count()
        
        # 📈 Тренды по месяцам (последние 6 месяцев)
        monthly_stats = []
        for i in range(6):
            date = datetime.now() - timedelta(days=30*i)
            start_month = date.replace(day=1)
            if i == 0:
                end_month = datetime.now()
            else:
                end_month = (start_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            users_count = db.query(User).filter(
                User.created_at >= start_month,
                User.created_at <= end_month
            ).count()
            
            monthly_stats.append({
                'month': calendar.month_name[start_month.month],
                'year': start_month.year,
                'users': users_count
            })
        
        monthly_stats.reverse()  # От старых к новым
        
        # 🌍 Статистика по источникам
        source_stats = db.query(
            User.source,
            func.count(User.id).label('count')
        ).group_by(User.source).all()
        
        source_data = [{'source': s.source or 'Неизвестно', 'count': s.count} for s in source_stats]
        
        # 🏠 Статистика недвижимости по типам
        property_stats = db.query(
            Property.deal_type,
            func.count(Property.id).label('count')
        ).group_by(Property.deal_type).all()
        
        property_data = [{'type': p.deal_type or 'Неизвестно', 'count': p.count} for p in property_stats]
        
        # 💰 Ценовая аналитика
        price_analysis = db.query(
            func.min(Property.price_usd).label('min_price'),
            func.max(Property.price_usd).label('max_price'),
            func.avg(Property.price_usd).label('avg_price')
        ).filter(Property.price_usd.isnot(None)).first()
        
        # 📍 Топ локаций
        location_stats = db.query(
            Property.city,
            func.count(Property.id).label('count')
        ).group_by(Property.city).order_by(func.count(Property.id).desc()).limit(10).all()
        
        location_data = [{'city': l.city or 'Неизвестно', 'count': l.count} for l in location_stats]
        
        # 📱 Контакты пользователей
        contact_stats = {
            'with_phone': db.query(User).filter(User.phone.isnot(None), User.phone != '').count(),
            'with_telegram': db.query(User).filter(User.telegram_id.isnot(None), User.telegram_id != '').count(),
            'with_whatsapp': db.query(User).filter(User.whatsapp_number.isnot(None), User.whatsapp_number != '').count(),
        }
        
        analytics_data = {
            'total_stats': {
                'users': total_users,
                'properties': total_properties,
                'projects': total_projects,
                'new_users_month': new_users_month
            },
            'monthly_trends': monthly_stats,
            'source_stats': source_data,
            'property_stats': property_data,
            'price_analysis': {
                'min_price': price_analysis.min_price if price_analysis else 0,
                'max_price': price_analysis.max_price if price_analysis else 0,
                'avg_price': round(price_analysis.avg_price, 2) if price_analysis and price_analysis.avg_price else 0
            },
            'location_stats': location_data,
            'contact_stats': contact_stats
        }
        
        return templates.TemplateResponse("admin/analytics.html", {
            "request": request,
            "analytics": analytics_data
        })
        
    except Exception as e:
        print(f"Ошибка в аналитике: {e}")
        return templates.TemplateResponse("admin/analytics.html", {
            "request": request,
            "analytics": {},
            "error": str(e)
        })

@router.get("/admin/reports")
async def reports_page(request: Request, db: Session = Depends(get_db)):
    """Страница отчетов"""
    try:
        # 📊 Быстрые отчеты
        reports_data = {
            'daily_registrations': await get_daily_registrations(db),
            'property_performance': await get_property_performance(db),
            'user_engagement': await get_user_engagement(db)
        }
        
        return templates.TemplateResponse("admin/reports.html", {
            "request": request,
            "reports": reports_data
        })
        
    except Exception as e:
        print(f"Ошибка в отчетах: {e}")
        return templates.TemplateResponse("admin/reports.html", {
            "request": request,
            "reports": {},
            "error": str(e)
        })

async def get_daily_registrations(db: Session) -> list:
    """Получить статистику регистраций по дням"""
    try:
        # Последние 7 дней
        data = []
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            start_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_day = start_day + timedelta(days=1)
            
            count = db.query(User).filter(
                User.created_at >= start_day,
                User.created_at < end_day
            ).count()
            
            data.append({
                'date': start_day.strftime('%d.%m'),
                'count': count
            })
        
        return list(reversed(data))
    except:
        return []

async def get_property_performance(db: Session) -> dict:
    """Анализ эффективности недвижимости"""
    try:
        total = db.query(Property).count()
        with_photos = db.query(Property).filter(Property.photos.isnot(None)).count()
        
        return {
            'total': total,
            'with_photos': with_photos,
            'completion_rate': round((with_photos / total * 100) if total > 0 else 0, 1)
        }
    except:
        return {'total': 0, 'with_photos': 0, 'completion_rate': 0}

async def get_user_engagement(db: Session) -> dict:
    """Анализ активности пользователей"""
    try:
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        
        return {
            'total': total_users,
            'active': active_users,
            'engagement_rate': round((active_users / total_users * 100) if total_users > 0 else 0, 1)
        }
    except:
        return {'total': 0, 'active': 0, 'engagement_rate': 0} 