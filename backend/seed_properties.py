# 📁 backend/seed_properties.py
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from models.property import Property

db: Session = SessionLocal()

property_1 = Property(
    title="1-комнатная у моря",
    description="Отличная квартира с видом на море",
    price=28000,
    location="Вонгамат",
    status="свободен",
    available_from=None,
    lat=12.965,
    lng=100.887
)

property_2 = Property(
    title="2-комнатная в центре",
    description="Удобная квартира рядом с инфраструктурой",
    price=35000,
    location="Центр",
    status="занят",
    available_from=None
)

db.add_all([property_1, property_2])
db.commit()
db.close()
