from backend.database import Base, engine
from routers.users import User  # импортируй модель

# Создание всех таблиц
Base.metadata.create_all(bind=engine)
