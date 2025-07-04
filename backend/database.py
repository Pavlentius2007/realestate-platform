import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql://user:pass@localhost/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={
        "client_encoding": "utf8",
        "options": "-c timezone=UTC -c client_encoding=UTF8"
    }
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# Импортируем все модели для автоматического создания таблиц
try:
    from backend.models.property import Property
    from backend.models.project import Project
    from backend.models.favorite import Favorite
    from backend.models.chat import ChatSession, ChatMessage
except ImportError:
    from models.property import Property
    from models.project import Project
    from models.favorite import Favorite
    from models.chat import ChatSession, ChatMessage

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Создает все таблицы в БД"""
    Base.metadata.create_all(bind=engine)