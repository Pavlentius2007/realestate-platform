from fastapi import APIRouter, Form
from backend.routers.user_tools import notify_telegram
# Используем современную систему переводов через ModernI18nMiddleware
from fastapi.responses import HTMLResponse
from fastapi import Request
from backend.config.templates import templates

router = APIRouter()

@router.post("/rent-request")
def submit_property(name: str = Form(...), phone: str = Form(...), property_title: str = Form(...)):
    message = (
        f"🏠 Новая заявка на сдачу объекта:\n"
        f"👤 Имя: {name}\n"
        f"📞 Телефон: {phone}\n"
        f"🏷️ Объект: {property_title}"
    )
    notify_telegram(message)
    return {"message": "Заявка отправлена!"}

@router.get("/add-property", response_class=HTMLResponse)
def add_property_form(request: Request):
    # Переводчик доступен автоматически через ModernI18nMiddleware
    return templates.TemplateResponse("add_property.html", {"request": request})
