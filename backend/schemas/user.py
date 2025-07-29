# 📁 backend/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    telegram_id: Optional[str] = None
    whatsapp_number: Optional[str] = None
    instagram_id: Optional[str] = None
    
    class Config:
        from_attributes = True

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    phone: Optional[str]
    source: Optional[str]
    telegram_id: Optional[str]
    whatsapp_number: Optional[str]
    instagram_id: Optional[str]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
