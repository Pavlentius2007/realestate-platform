# backend/create_tables.py
from backend.database import Base, engine
from routers.users import User  # импорт модели

Base.metadata.create_all(bind=engine)
