from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from backend.database import Base
from sqlalchemy.dialects.postgresql import ARRAY

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    subtitle = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    district = Column(String, nullable=True)
    
    # Основные характеристики
    developer = Column(String, nullable=True)  # Застройщик
    completion_year = Column(Integer, nullable=True)  # Год завершения
    total_units = Column(Integer, nullable=True)  # Общее количество единиц
    floors = Column(Integer, nullable=True)  # Количество этажей
    
    # Цены
    price_from = Column(Float, nullable=True)  # Цена от
    price_to = Column(Float, nullable=True)    # Цена до
    currency = Column(String, default="THB", nullable=True)
    
    # Координаты
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    
    # Изображения и медиа
    hero_image = Column(String, nullable=True)  # Главное изображение
    gallery_images = Column(ARRAY(String), nullable=True)  # Галерея изображений
    video_url = Column(String, nullable=True)  # Ссылка на видео
    
    # Особенности и удобства
    highlights = Column(ARRAY(String), nullable=True)  # Основные преимущества
    amenities = Column(ARRAY(String), nullable=True)   # Удобства
    
    # Планировки и типы квартир
    unit_types = Column(Text, nullable=True)  # JSON с типами квартир
    
    # Платежи и инвестиции
    payment_plan = Column(Text, nullable=True)  # План платежей
    down_payment = Column(String, nullable=True)  # Первоначальный взнос
    monthly_payment = Column(String, nullable=True)  # Ежемесячный платеж
    roi_info = Column(Text, nullable=True)  # Информация о ROI
    
    # Контактная информация
    sales_office_address = Column(String, nullable=True)
    sales_office_phone = Column(String, nullable=True)
    sales_office_email = Column(String, nullable=True)
    
    # Статус проекта
    status = Column(String, default="active", nullable=True)  # active, completed, upcoming
    is_featured = Column(Boolean, default=False)  # Рекомендуемый проект
    
    # Мета-информация
    meta_title = Column(String, nullable=True)
    meta_description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Project(slug='{self.slug}', title='{self.title}')>" 