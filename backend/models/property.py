from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from backend.database import Base
from sqlalchemy.dialects.postgresql import ARRAY

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    condo_name = Column(String, nullable=True)
    property_type = Column("type", String, nullable=True)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    price_period = Column(String, nullable=True)
    location = Column(String, nullable=True)
    district = Column(String, nullable=True)
    area = Column(Float, nullable=True)
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Integer, nullable=True)
    floor = Column(String, nullable=True)
    furnished = Column(String, nullable=True)
    published_at = Column(String, nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    features = Column(ARRAY(String), nullable=True)
    status = Column(String, nullable=True)
    land_area = Column(Float, nullable=True)
    old_price = Column(Float, nullable=True)
    is_new_building = Column(Boolean, default=False, nullable=True)
    
    # Дополнительные поля для всех типов недвижимости
    deal_type = Column(String, nullable=True)  # buy или rent
    currency = Column(String, default="THB", nullable=True)  # Валюта цены
    short_description = Column(String, nullable=True)  # Краткое описание
    contact_phone = Column(String, nullable=True)  # Контактный телефон
    whatsapp = Column(String, nullable=True)  # WhatsApp контакт
    amenities = Column(String, nullable=True)  # Удобства (строка через запятую)
    
    # Поля для управления арендой
    rental_status = Column(String, default="available", nullable=True)  # available, rented, maintenance
    rental_start_date = Column(DateTime, nullable=True)  # Дата начала аренды
    rental_end_date = Column(DateTime, nullable=True)    # Дата окончания аренды
    renter_name = Column(String, nullable=True)          # Имя арендатора
    renter_contact = Column(String, nullable=True)       # Контакт арендатора
    rental_notes = Column(String, nullable=True)         # Заметки по аренде
    
    images = relationship("PropertyImage", back_populates="property", cascade="all, delete-orphan")

    @property
    def main_image_url(self):
        if self.images:
            return self.images[0].image_url
        return None
