from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from backend.database import Base  # ✅



class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)  # Теперь обязательное
    hashed_password = Column(String, nullable=False)  # Обязательное поле для паролей
    name = Column(String, nullable=False, default="Пользователь")  # NOT NULL после миграции

    # 👇 Основные поля пользователя
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    source = Column(String, nullable=True)  # Например: "сайт", "реклама", "Telegram", "рекомендация"
    telegram_id = Column(String, nullable=True)  # Telegram user ID
    whatsapp_number = Column(String, nullable=True)  # WhatsApp phone number
    instagram_id = Column(String, nullable=True)  # Instagram user ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 👇 Дополнительные поля для CRM
    budget_min = Column(Integer, nullable=True)  # Минимальный бюджет клиента
    budget_max = Column(Integer, nullable=True)  # Максимальный бюджет клиента
    city = Column(String, nullable=True)  # Город клиента
    country = Column(String, nullable=True)  # Страна клиента
    property_type = Column(String, nullable=True)  # Предпочитаемый тип недвижимости
    notes = Column(String, nullable=True)  # Заметки менеджера
    priority = Column(String, nullable=True, default="medium")  # Приоритет лида
    status = Column(String, nullable=True, default="new")  # Статус лида
    
    # Дополнительные поля для совместимости с БД
    is_active = Column(Boolean, nullable=True, default=True)  # Статус активности
    last_contact = Column(DateTime(timezone=True), nullable=True)  # Последний контакт
