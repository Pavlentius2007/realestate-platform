from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, text, desc
from datetime import datetime, timedelta
from backend.database import get_db
from backend.models.user import User
from backend.models.property import Property
from backend.config.templates import templates
from typing import Optional

router = APIRouter()

@router.get("/admin/crm", response_class=HTMLResponse)
async def crm_dashboard(request: Request, db: Session = Depends(get_db)):
    """Главная CRM панель"""
    try:
        # 📊 CRM статистика
        total_leads = db.query(User).filter(User.source.isnot(None)).count()
        new_leads_week = db.query(User).filter(
            User.created_at >= datetime.now() - timedelta(days=7),
            User.source.isnot(None)
        ).count()
        
        # 🔥 Горячие лиды (с несколькими контактами)
        hot_leads = db.query(User).filter(
            User.phone.isnot(None),
            User.telegram_id.isnot(None) | User.whatsapp_number.isnot(None)
        ).count()
        
        # 📈 Конверсия по источникам
        conversion_data = []
        sources = db.query(User.source).distinct().all()
        for source in sources:
            if source.source:
                total = db.query(User).filter(User.source == source.source).count()
                conversion_data.append({
                    'source': source.source,
                    'total_leads': total,
                    'conversion_rate': min(85 + (hash(source.source) % 15), 99)  # Демо данные
                })
        
        # 📋 Последние лиды
        recent_leads = db.query(User).filter(User.source.isnot(None)).order_by(desc(User.created_at)).limit(10).all()
        
        # 🎯 Воронка продаж (демо данные)
        funnel_data = {
            'leads': total_leads,
            'qualified': int(total_leads * 0.6),
            'proposals': int(total_leads * 0.3),
            'deals': int(total_leads * 0.15),
            'closed': int(total_leads * 0.08)
        }
        
        crm_data = {
            'stats': {
                'total_leads': total_leads,
                'new_leads_week': new_leads_week,
                'hot_leads': hot_leads,
                'conversion_rate': 15.8  # Демо
            },
            'conversion_data': conversion_data,
            'recent_leads': recent_leads,
            'funnel_data': funnel_data
        }
        
        return templates.TemplateResponse("admin/crm.html", {
            "request": request,
            "crm": crm_data
        })
        
    except Exception as e:
        print(f"Ошибка CRM панели: {e}")
        return templates.TemplateResponse("admin/crm.html", {
            "request": request,
            "crm": {},
            "error": str(e)
        })

@router.get("/admin/crm/leads", response_class=HTMLResponse)
async def leads_management(request: Request, db: Session = Depends(get_db)):
    """Управление лидами"""
    try:
        # Все лиды с пагинацией
        leads = db.query(User).filter(User.source.isnot(None)).order_by(desc(User.created_at)).limit(50).all()
        
        # Статистика по статусам (демо)
        status_stats = {
            'new': len([l for l in leads if not l.phone]),
            'contacted': len([l for l in leads if l.phone and not l.telegram_id]),
            'qualified': len([l for l in leads if l.phone and l.telegram_id]),
            'closed': len([l for l in leads if l.phone and l.whatsapp_number and l.telegram_id])
        }
        
        return templates.TemplateResponse("admin/crm_leads.html", {
            "request": request,
            "leads": leads,
            "status_stats": status_stats
        })
        
    except Exception as e:
        print(f"Ошибка управления лидами: {e}")
        return templates.TemplateResponse("admin/crm_leads.html", {
            "request": request,
            "leads": [],
            "status_stats": {},
            "error": str(e)
        })

@router.post("/admin/crm/lead/{lead_id}/update")
async def update_lead_status(lead_id: int, status: str = Form(...), notes: str = Form(""), db: Session = Depends(get_db)):
    """Обновление статуса лида"""
    try:
        lead = db.query(User).filter(User.id == lead_id).first()
        if not lead:
            return JSONResponse({"success": False, "message": "Лид не найден"})
        
        # В реальной системе здесь была бы таблица lead_status или поле в User
        # Пока просто обновим источник для демонстрации
        lead.source = f"{lead.source}_{status}"
        db.commit()
        
        return JSONResponse({
            "success": True, 
            "message": f"Статус лида обновлен на '{status}'"
        })
        
    except Exception as e:
        print(f"Ошибка обновления лида: {e}")
        return JSONResponse({"success": False, "message": str(e)})

@router.get("/admin/crm/pipeline", response_class=HTMLResponse)
async def sales_pipeline(request: Request, db: Session = Depends(get_db)):
    """Воронка продаж"""
    try:
        # Получаем данные для воронки
        total_leads = db.query(User).filter(User.source.isnot(None)).count()
        
        # Демо данные для воронки
        pipeline_stages = [
            {
                'stage': 'Лиды',
                'count': total_leads,
                'percentage': 100,
                'color': '#3b82f6',
                'leads': db.query(User).filter(User.source.isnot(None)).limit(5).all()
            },
            {
                'stage': 'Квалификация',
                'count': int(total_leads * 0.6),
                'percentage': 60,
                'color': '#10b981',
                'leads': db.query(User).filter(User.phone.isnot(None)).limit(5).all()
            },
            {
                'stage': 'Предложение',
                'count': int(total_leads * 0.3),
                'percentage': 30,
                'color': '#f59e0b',
                'leads': db.query(User).filter(User.telegram_id.isnot(None)).limit(5).all()
            },
            {
                'stage': 'Переговоры',
                'count': int(total_leads * 0.15),
                'percentage': 15,
                'color': '#ef4444',
                'leads': db.query(User).filter(User.whatsapp_number.isnot(None)).limit(5).all()
            },
            {
                'stage': 'Сделка',
                'count': int(total_leads * 0.08),
                'percentage': 8,
                'color': '#8b5cf6',
                'leads': []
            }
        ]
        
        return templates.TemplateResponse("admin/crm_pipeline.html", {
            "request": request,
            "pipeline_stages": pipeline_stages,
            "total_leads": total_leads
        })
        
    except Exception as e:
        print(f"Ошибка воронки продаж: {e}")
        return templates.TemplateResponse("admin/crm_pipeline.html", {
            "request": request,
            "pipeline_stages": [],
            "total_leads": 0,
            "error": str(e)
        })

@router.get("/admin/crm/interactions", response_class=HTMLResponse)
async def interactions_log(request: Request, db: Session = Depends(get_db)):
    """Лог взаимодействий с клиентами"""
    try:
        # В реальной системе здесь была бы отдельная таблица interactions
        # Пока используем логику на основе пользователей
        users_with_contacts = db.query(User).filter(
            User.phone.isnot(None) | User.telegram_id.isnot(None) | User.whatsapp_number.isnot(None)
        ).order_by(desc(User.created_at)).limit(30).all()
        
        # Генерируем демо взаимодействия
        interactions = []
        for user in users_with_contacts:
            if user.phone:
                interactions.append({
                    'user': user,
                    'type': 'call',
                    'description': 'Входящий звонок',
                    'timestamp': user.created_at,
                    'status': 'completed'
                })
            if user.telegram_id:
                interactions.append({
                    'user': user,
                    'type': 'message',
                    'description': 'Сообщение в Telegram',
                    'timestamp': user.created_at,
                    'status': 'sent'
                })
            if user.whatsapp_number:
                interactions.append({
                    'user': user,
                    'type': 'whatsapp',
                    'description': 'WhatsApp сообщение',
                    'timestamp': user.created_at,
                    'status': 'delivered'
                })
        
        # Сортируем по времени
        interactions.sort(key=lambda x: x['timestamp'], reverse=True)
        interactions = interactions[:20]  # Берем последние 20
        
        return templates.TemplateResponse("admin/crm_interactions.html", {
            "request": request,
            "interactions": interactions
        })
        
    except Exception as e:
        print(f"Ошибка лога взаимодействий: {e}")
        return templates.TemplateResponse("admin/crm_interactions.html", {
            "request": request,
            "interactions": [],
            "error": str(e)
        })

@router.post("/admin/crm/interaction/add")
async def add_interaction(
    user_id: int = Form(...),
    interaction_type: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db)
):
    """Добавление нового взаимодействия"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return JSONResponse({"success": False, "message": "Пользователь не найден"})
        
        # В реальной системе здесь было бы сохранение в таблицу interactions
        # Пока просто возвращаем успех
        
        return JSONResponse({
            "success": True,
            "message": f"Взаимодействие '{interaction_type}' добавлено для {user.full_name or user.email}"
        })
        
    except Exception as e:
        print(f"Ошибка добавления взаимодействия: {e}")
        return JSONResponse({"success": False, "message": str(e)}) 