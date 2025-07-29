# backend/routers/user_tools.py
import gspread
import requests
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import os
# Используем современную систему переводов через ModernI18nMiddleware
from backend.config.templates import templates
from fastapi import APIRouter, Request, Form, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from backend.models.user import User
from backend.database import SessionLocal
import requests as pyrequests

BOT_TOKEN = "7911446289:AAG5RzcItFlL6RllKRL3paU9NmYnqs8-SDI"
CHAT_ID = "1262412157"
GOOGLE_SHEETS_CREDENTIALS = os.path.abspath("C:/Users/mishi/Сайт/realestate-platform/backend/routers/fastapi-users-462815-d6c34495b9cd.json")
GOOGLE_SHEET_NAME = "UserRegistrations"
INSTAGRAM_CLIENT_ID = "1168971138589257"
INSTAGRAM_CLIENT_SECRET = "f5afa10f03b687adef0552e86dbe5de5"
INSTAGRAM_REDIRECT_URI = "http://127.0.0.1:8000/auth/instagram/callback"

router = APIRouter()

SUPPORTED_LANGUAGES = ["ru", "en", "th", "zh"]  # или импортировать из config
DEFAULT_LANGUAGE = "ru"
LANGUAGE_SESSION_KEY = "lang"
LANGUAGE_COOKIE_NAME = "lang"

@router.get("/auth/telegram", response_class=HTMLResponse)
def telegram_login(request: Request):
    return templates.TemplateResponse("auth_telegram.html", {"request": request})

@router.post("/auth/telegram/callback", response_class=HTMLResponse)
def telegram_callback(request: Request, telegram_id: str = Form(...), full_name: str = Form(None)):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user:
        if full_name:
            setattr(user, 'full_name', full_name)
    else:
        user = User(telegram_id=telegram_id, full_name=full_name, source="Telegram")
        db.add(user)
    db.commit()
    db.close()
    return templates.TemplateResponse("thank_you.html", {"request": request, "message": "Вы успешно авторизованы через Telegram!"})

@router.get("/auth/whatsapp", response_class=HTMLResponse)
def whatsapp_form(request: Request):
    return templates.TemplateResponse("auth_whatsapp.html", {"request": request})

@router.post("/auth/whatsapp/submit", response_class=HTMLResponse)
def whatsapp_submit(request: Request, whatsapp_number: str = Form(...), full_name: str = Form(None)):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.whatsapp_number == whatsapp_number).first()
    if user:
        if full_name:
            setattr(user, 'full_name', full_name)
    else:
        user = User(whatsapp_number=whatsapp_number, full_name=full_name, source="WhatsApp")
        db.add(user)
    db.commit()
    db.close()
    return templates.TemplateResponse("thank_you.html", {"request": request, "message": "Ваш WhatsApp успешно сохранён!"})

def notify_telegram(message: str):
    """
    Отправляет сообщение в Telegram с подробным логированием
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
    
    try:
        print(f"🔔 Отправка в Telegram: {message[:100]}...")
        response = requests.post(url, data=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print("✅ Telegram: Сообщение отправлено успешно")
                return True
            else:
                print(f"❌ Telegram API Error: {result}")
                return False
        else:
            print(f"❌ Telegram HTTP Error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Telegram: Таймаут при отправке сообщения")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Telegram Request Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Telegram Unexpected Error: {e}")
        return False


def notify_user_registration(user):
    message = (
        f"📩 Новый пользователь\n"
        f"📧 Email: {user.email}\n"
        f"👤 Имя: {user.full_name or '-'}\n"
        f"📞 Телефон: {user.phone or '-'}\n"
        f"🌐 Источник: {user.source or '-'}"
    )
    notify_telegram(message)
    notify_google_sheets(user)


def notify_google_sheets(user):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEETS_CREDENTIALS, scope)
        client = gspread.authorize(creds)
        sheet = client.open(GOOGLE_SHEET_NAME).sheet1
        sheet.append_row([
            user.email,
            user.full_name or "",
            user.phone or "",
            user.source or "",
            datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        ])
    except Exception as e:
        print(f"[Google Sheets Error] {e}")


# Специализированные уведомления

def notify_rent_submission(data):
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    message = (
        f"🏠 Новая заявка на сдачу недвижимости\n"
        f"📍 Адрес: {data.address}\n"
        f"🔢 Комнат: {data.rooms}\n"
        f"📈 Этаж: {data.floor}\n"
        f"💰 Стоимость: {data.price} THB\n"
        f"📱 Телефон клиента: {data.phone}\n"
        f"🕒 Время: {now}"
    )
    notify_telegram(message)


def notify_rent_request(data):
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    message = (
        f"🔍 Заявка на аренду\n"
        f"👤 Имя: {data.name}\n"
        f"📱 Телефон: {data.phone}\n"
        f"📍 Пожелания: {data.comment or 'Не указано'}\n"
        f"🕒 Время: {now}"
    )
    notify_telegram(message)


def notify_new_project_interest(data):
    message = (
        f"🏗️ Заявка по новостройке\n"
        f"👤 Имя: {data.name}\n"
        f"📱 Телефон: {data.phone}"
    )
    notify_telegram(message)


def notify_boi_interest(data):
    message = (
        f"📈 Заявка по проекту BOI\n"
        f"👤 Имя: {data.name}\n"
        f"📱 Телефон: {data.phone}\n"
        f"💬 Комментарий: {data.comment or 'Нет'}"
    )
    notify_telegram(message)

@router.get("/auth/instagram")
def instagram_oauth_start():
    url = (
        f"https://api.instagram.com/oauth/authorize"
        f"?client_id={INSTAGRAM_CLIENT_ID}"
        f"&redirect_uri={INSTAGRAM_REDIRECT_URI}"
        f"&scope=user_profile"
        f"&response_type=code"
    )
    return RedirectResponse(url)

@router.get("/auth/instagram/callback", response_class=HTMLResponse)
def instagram_oauth_callback(request: Request, code: str = None):
    if not code:
        return templates.TemplateResponse("thank_you.html", {"request": request, "message": "Ошибка авторизации Instagram."})
    # Получаем access_token
    token_url = "https://api.instagram.com/oauth/access_token"
    data = {
        "client_id": INSTAGRAM_CLIENT_ID,
        "client_secret": INSTAGRAM_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": INSTAGRAM_REDIRECT_URI,
        "code": code,
    }
    resp = pyrequests.post(token_url, data=data)
    if resp.status_code != 200:
        return templates.TemplateResponse("thank_you.html", {"request": request, "message": "Ошибка получения токена Instagram."})
    token_data = resp.json()
    instagram_id = token_data.get("user_id")
    # Сохраняем instagram_id в базу
    db: Session = SessionLocal()
    user = db.query(User).filter(User.instagram_id == str(instagram_id)).first()
    if not user:
        user = User(instagram_id=str(instagram_id), source="Instagram")
        db.add(user)
    db.commit()
    db.close()
    return templates.TemplateResponse("thank_you.html", {"request": request, "message": "Вы успешно авторизованы через Instagram!"})

@router.post("/auth/instagram/submit", response_class=HTMLResponse)
def instagram_submit(request: Request, instagram_id: str = Form(...), full_name: str = Form(None)):
    db: Session = SessionLocal()
    user = db.query(User).filter(User.instagram_id == instagram_id).first()
    if user:
        if full_name:
            setattr(user, 'full_name', full_name)
    else:
        user = User(instagram_id=instagram_id, full_name=full_name, source="Instagram")
        db.add(user)
    db.commit()
    db.close()
    return templates.TemplateResponse("thank_you.html", {"request": request, "message": "Ваш профиль Instagram сохранён!"})

@router.get("/set-language")
async def set_language(request: Request, lang: str, next: str = "/"):
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    # Сохраняем язык в сессию
    try:
        request.session[LANGUAGE_SESSION_KEY] = lang
    except Exception as e:
        print(f"Ошибка сохранения языка в сессию: {e}")
    # Готовим редирект
    url = next if next else request.headers.get("referer") or "/"
    if not url:
        url = "/"
    response = RedirectResponse(url=str(url), status_code=status.HTTP_302_FOUND)
    # Сохраняем язык в cookie
    response.set_cookie(key=LANGUAGE_COOKIE_NAME, value=lang, max_age=60*60*24*365, httponly=True)
    return response
