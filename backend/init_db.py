from backend.database import Base, engine
from backend.models.property import Property

print("Создаём таблицы в базе...")
Base.metadata.create_all(bind=engine)
print("✅ Таблицы созданы.")
