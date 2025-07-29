from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base
from datetime import datetime
from typing import Dict, Optional, List

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False, index=True)  # Сессия пользователя (для анонимных пользователей)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Отношения
    property = relationship("Property", backref="favorites")

    def translate_property_fields(self, property_data: Dict, target_langs: Optional[List[str]] = None) -> Dict:
        if target_langs is None:
            target_langs = ['en', 'th', 'zh']
        # ... ваша логика ...
        return {} 