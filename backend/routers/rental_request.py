from fastapi import APIRouter, Form, Depends
from backend.routers.user_tools import notify_telegram
# Используем современную систему переводов через ModernI18nMiddleware
from fastapi.responses import HTMLResponse
from fastapi import Request
from backend.config.templates import templates
from sqlalchemy.orm import Session
from backend.models.user import User
from backend.database import SessionLocal, get_db
from typing import Optional

router = APIRouter()

@router.post("/rental-request")
def handle_rental_request(
    name: str = Form(...), 
    phone: str = Form(...), 
    whatsapp: str = Form(""),
    telegram: str = Form(""),
    property_name: str = Form(""),
    check_in_date: str = Form(""),
    check_out_date: str = Form(""),
    guests: str = Form(""),
    message: str = Form(""),
    db: Session = Depends(get_db)
):
    from datetime import datetime
    
    try:
        # Сохраняем пользователя в базу данных (исправлены названия полей)
        user = User(
            full_name=name,  # Исправлено: name -> full_name
            phone=phone if phone else None,
            whatsapp_number=whatsapp if whatsapp else None,  # Исправлено: whatsapp -> whatsapp_number
            telegram_id=telegram if telegram else None,  # Исправлено: telegram -> telegram_id
            source="rental_request",
            is_active=True  # Исправлено: "true" -> True (булевое значение)
        )
        db.add(user)
        db.commit()
        
        # Формируем детальное сообщение для Telegram
        text = (
            f"🏖️ НОВАЯ ЗАЯВКА НА АРЕНДУ\n\n"
            f"👤 Клиент: {name}\n"
            f"📞 Телефон: {phone}\n"
        )
        
        if whatsapp:
            text += f"📱 WhatsApp: {whatsapp}\n"
        if telegram:
            text += f"✈️ Telegram: {telegram}\n"
        
        if property_name:
            text += f"🏠 Объект: {property_name}\n"
        
        if check_in_date and check_out_date:
            text += f"📅 Даты: {check_in_date} - {check_out_date}\n"
        
        if guests:
            text += f"👥 Количество гостей: {guests}\n"
        
        if message:
            text += f"💬 Комментарий: {message}\n"
        
        text += f"\n🕒 Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        text += f"\n📊 ID пользователя: {user.id}"
        
        notify_telegram(text)
        
        return {"message": "Заявка отправлена!"}
        
    except Exception as e:
        print(f"Ошибка при обработке заявки на аренду: {e}")
        db.rollback()
        return {"message": "Ошибка при отправке заявки", "error": str(e)}

@router.get("/rental-request", response_class=HTMLResponse)
def rental_request_form(request: Request):
    # Переводчик доступен автоматически через ModernI18nMiddleware
    return templates.TemplateResponse("rental_request.html", {"request": request})

@router.post("/auth/telegram/callback", response_class=HTMLResponse)
def telegram_callback(request: Request, telegram_id: str = Form(...), full_name: Optional[str] = Form(None)):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user:
        user.full_name = full_name or user.full_name
    else:
        user = User(telegram_id=telegram_id, full_name=full_name, source="Telegram")
        db.add(user)
    db.commit()
    db.close()
    return templates.TemplateResponse("thank_you.html", {"request": request, "message": "Вы успешно авторизованы через Telegram!"})

@router.post("/auth/whatsapp/submit", response_class=HTMLResponse)
def whatsapp_submit(request: Request, whatsapp_number: str = Form(...), full_name: Optional[str] = Form(None)):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.whatsapp_number == whatsapp_number).first()
    if user:
        user.full_name = full_name or user.full_name
    else:
        user = User(whatsapp_number=whatsapp_number, full_name=full_name, source="WhatsApp")
        db.add(user)
    db.commit()
    db.close()
    return templates.TemplateResponse("thank_you.html", {"request": request, "message": "Ваш WhatsApp успешно сохранён!"})
