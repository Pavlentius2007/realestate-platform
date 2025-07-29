from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:admin@localhost:5432/thailand_realty")

with engine.connect() as conn:
    print("✅ Успешное подключение к базе")
