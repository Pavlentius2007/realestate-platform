from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

# Используем относительный импорт для избежания циклических зависимостей
try:
    from backend.database import Base
except ImportError:
    from database import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True)  # UUID для сессии
    user_preferences = Column(JSON)  # Предпочтения пользователя
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связь с сообщениями
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), ForeignKey("chat_sessions.session_id"))
    message_type = Column(String(50))  # 'user' или 'assistant'
    content = Column(Text)
    extra_data = Column(JSON)  # Дополнительные данные (найденные объекты, параметры поиска и т.д.)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Связь с сессией
    session = relationship("ChatSession", back_populates="messages") 