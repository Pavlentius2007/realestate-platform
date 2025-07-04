from fastapi import APIRouter, Form, HTTPException
from datetime import datetime
from backend.routers.user_tools import notify_telegram

router = APIRouter()

@router.post("/submit-property")
async def submit_property(
    name: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    rooms: int = Form(...),
    floor: str = Form(...),
    price: str = Form(...)
):
    try:
        message = (
            f"📤 Новая заявка на сдачу объекта\n\n"
            f"👤 Клиент: {name}\n"
            f"📞 Телефон: {phone}\n"
            f"📍 Адрес: {address}\n"
            f"🛏 Комнат: {rooms}\n"
            f"🏢 Этаж: {floor}\n"
            f"💸 Цена аренды: {price} THB\n"
            f"🕒 Время: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
        notify_telegram(message)
        return {"message": "Заявка успешно отправлена"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка отправки: {str(e)}")
