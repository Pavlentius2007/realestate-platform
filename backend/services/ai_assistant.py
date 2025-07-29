import re
import json
import uuid
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime

try:
    from backend.models.property import Property
    from backend.models.chat import ChatSession, ChatMessage
except ImportError:
    from models.property import Property
    from models.chat import ChatSession, ChatMessage

class RealEstateAIAssistant:
    """Умный ИИ-помощник для подбора недвижимости"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Словари для понимания пользователя
        self.budget_keywords = {
            'до': 'max', 'не больше': 'max', 'максимум': 'max', 'лимит': 'max',
            'от': 'min', 'не меньше': 'min', 'минимум': 'min', 'начиная': 'min',
            'около': 'around', 'примерно': 'around', 'приблизительно': 'around'
        }
        
        self.property_types = {
            'квартира': 'apartment', 'апартаменты': 'apartment', 'кондо': 'condo',
            'вилла': 'villa', 'дом': 'house', 'таунхаус': 'townhouse',
            'студия': 'studio', 'пентхаус': 'penthouse'
        }
        
        self.districts = {
            'центр': 'central_pattaya', 'центральная': 'central_pattaya',
            'север': 'north_pattaya', 'северная': 'north_pattaya',
            'юг': 'south_pattaya', 'южная': 'south_pattaya',
            'джомтьен': 'jomtien', 'наклуа': 'naklua', 'вонгамат': 'wong_amat',
            'пратамнак': 'pratamnak'
        }
        
        self.amenities_keywords = {
            'бассейн': 'pool', 'спортзал': 'gym', 'фитнес': 'gym',
            'парковка': 'parking', 'охрана': 'security', 'лифт': 'elevator',
            'балкон': 'balcony', 'терраса': 'terrace', 'кондиционер': 'ac'
        }
        
        self.view_keywords = {
            'море': 'sea', 'океан': 'sea', 'вода': 'sea',
            'город': 'city', 'горы': 'mountain', 'сад': 'garden', 'парк': 'garden'
        }

    def get_or_create_session(self, session_id: str = None) -> ChatSession:
        """Получает или создает сессию чата"""
        if not session_id:
            session_id = str(uuid.uuid4())
            
        session = self.db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if not session:
            session = ChatSession(
                session_id=session_id,
                user_preferences={}
            )
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
        
        return session

    def parse_user_message(self, message: str) -> Dict[str, Any]:
        """Анализирует сообщение пользователя и извлекает параметры поиска"""
        message_lower = message.lower()
        
        search_params = {}
        
        # Извлекаем бюджет
        budget_match = re.search(r'(\d+(?:\s?\d+)*)\s*(?:тысяч|млн|k|тыс|бат|฿)', message_lower)
        if budget_match:
            amount = int(budget_match.group(1).replace(' ', ''))
            if 'млн' in message_lower:
                amount *= 1000000
            elif any(word in message_lower for word in ['тысяч', 'тыс', 'k']):
                amount *= 1000
            search_params['budget'] = amount
        
        # Извлекаем тип недвижимости
        for keyword, prop_type in self.property_types.items():
            if keyword in message_lower:
                search_params['property_type'] = prop_type
                break
        
        # Извлекаем район
        for keyword, district in self.districts.items():
            if keyword in message_lower:
                search_params['district'] = district
                break
        
        # Извлекаем количество спален
        bedrooms_match = re.search(r'(\d+)\s*(?:спальн|комнат|bedroom)', message_lower)
        if bedrooms_match:
            search_params['bedrooms'] = int(bedrooms_match.group(1))
        
        # Извлекаем площадь
        area_match = re.search(r'(\d+)\s*(?:м²|кв\.м|метр)', message_lower)
        if area_match:
            search_params['area'] = int(area_match.group(1))
        
        # Извлекаем удобства
        amenities = []
        for keyword, amenity in self.amenities_keywords.items():
            if keyword in message_lower:
                amenities.append(amenity)
        if amenities:
            search_params['amenities'] = amenities
        
        # Извлекаем вид
        for keyword, view in self.view_keywords.items():
            if keyword in message_lower:
                search_params['view'] = view
                break
        
        # Анализируем цель (инвестиции, жизнь, отдых)
        if any(word in message_lower for word in ['инвест', 'доход', 'сдача', 'прибыль']):
            search_params['purpose'] = 'investment'
        elif any(word in message_lower for word in ['жить', 'пмж', 'переезд', 'постоянно']):
            search_params['purpose'] = 'living'
        elif any(word in message_lower for word in ['отдых', 'отпуск', 'туризм', 'каникулы']):
            search_params['purpose'] = 'vacation'
        
        return search_params

    def search_properties(self, params: Dict[str, Any]) -> List[Property]:
        """Ищет недвижимость по параметрам"""
        query = self.db.query(Property)
        
        # Фильтрация по бюджету
        if 'budget' in params:
            query = query.filter(Property.price <= params['budget'])
        
        # Фильтрация по типу недвижимости
        if 'property_type' in params:
            query = query.filter(Property.property_type == params['property_type'])
        
        # Фильтрация по району
        if 'district' in params:
            query = query.filter(Property.district == params['district'])
        
        # Фильтрация по количеству спален
        if 'bedrooms' in params:
            query = query.filter(Property.bedrooms >= params['bedrooms'])
        
        # Фильтрация по площади
        if 'area' in params:
            query = query.filter(Property.area >= params['area'])
        
        # Фильтрация по виду
        if 'view' in params:
            view_keyword = params['view']
            if view_keyword == 'sea':
                query = query.filter(Property.description.ilike('%море%'))
            elif view_keyword == 'city':
                query = query.filter(Property.description.ilike('%город%'))
            elif view_keyword == 'mountain':
                query = query.filter(Property.description.ilike('%гор%'))
        
        # Фильтрация по удобствам
        if 'amenities' in params:
            for amenity in params['amenities']:
                if amenity == 'pool':
                    query = query.filter(Property.description.ilike('%бассейн%'))
                elif amenity == 'gym':
                    query = query.filter(Property.description.ilike('%спортзал%'))
                elif amenity == 'parking':
                    query = query.filter(Property.description.ilike('%парков%'))
        
        # Ограничиваем результаты
        return query.limit(20).all()

    def generate_response(self, user_message: str, found_properties: List[Property], 
                         search_params: Dict[str, Any], session: ChatSession) -> str:
        """Генерирует умный ответ на основе найденных объектов"""
        
        if not found_properties:
            return self._generate_no_results_response(search_params)
        
        # Анализируем найденные объекты
        total_count = len(found_properties)
        avg_price = sum(p.price for p in found_properties if p.price) // total_count
        price_range = {
            'min': min(p.price for p in found_properties if p.price),
            'max': max(p.price for p in found_properties if p.price)
        }
        
        # Формируем умный ответ
        response_parts = []
        
        # Приветствие и краткая статистика
        response_parts.append(f"🤖 Отлично! Я нашел {total_count} подходящих вариантов недвижимости.")
        
        # Анализ по цене
        if 'budget' in search_params:
            budget = search_params['budget']
            if avg_price < budget * 0.8:
                response_parts.append(f"💰 Хорошие новости! Средняя цена ({avg_price:,.0f} ฿) ниже вашего бюджета.")
            elif avg_price > budget:
                response_parts.append(f"📊 Средняя цена немного выше бюджета, но есть варианты от {price_range['min']:,.0f} ฿.")
        
        # Рекомендации по типу недвижимости
        property_types_found = {}
        for prop in found_properties:
            ptype = prop.property_type
            if ptype not in property_types_found:
                property_types_found[ptype] = 0
            property_types_found[ptype] += 1
        
        if len(property_types_found) > 1:
            most_common = max(property_types_found.items(), key=lambda x: x[1])
            response_parts.append(f"🏠 Больше всего вариантов типа '{most_common[0]}' ({most_common[1]} шт.)")
        
        # Рекомендации по району
        districts_found = {}
        for prop in found_properties:
            if prop.district:
                if prop.district not in districts_found:
                    districts_found[prop.district] = 0
                districts_found[prop.district] += 1
        
        if districts_found:
            top_district = max(districts_found.items(), key=lambda x: x[1])
            response_parts.append(f"📍 Самый популярный район: {top_district[0]} ({top_district[1]} объектов)")
        
        # Персональные рекомендации
        if 'purpose' in search_params:
            purpose = search_params['purpose']
            if purpose == 'investment':
                response_parts.append("💼 Для инвестиций рекомендую обратить внимание на новостройки с хорошей инфраструктурой.")
            elif purpose == 'living':
                response_parts.append("🏡 Для постоянного проживания важны школы, больницы и магазины поблизости.")
            elif purpose == 'vacation':
                response_parts.append("🏖️ Для отдыха лучше выбрать место рядом с пляжем и развлечениями.")
        
        # Топ-3 рекомендации
        top_properties = sorted(found_properties, key=lambda p: (
            p.price if p.price else 999999999,  # Сортировка по цене
            -p.area if p.area else 0  # И по площади (больше = лучше)
        ))[:3]
        
        response_parts.append("🌟 Мои топ-рекомендации:")
        for i, prop in enumerate(top_properties, 1):
            price_str = f"{prop.price:,.0f} ฿" if prop.price else "Цена не указана"
            area_str = f"{prop.area} м²" if prop.area else "Площадь не указана"
            response_parts.append(f"{i}. {prop.title} - {price_str}, {area_str}")
        
        response_parts.append("\n💬 Хотите узнать больше о каком-то объекте? Или изменить параметры поиска?")
        
        return "\n\n".join(response_parts)

    def _generate_no_results_response(self, search_params: Dict[str, Any]) -> str:
        """Генерирует ответ когда ничего не найдено"""
        response_parts = [
            "🤔 К сожалению, я не нашел точных совпадений по вашим критериям.",
            "",
            "💡 Предлагаю несколько вариантов:"
        ]
        
        suggestions = []
        
        if 'budget' in search_params:
            budget = search_params['budget']
            suggestions.append(f"• Увеличить бюджет до {budget * 1.2:,.0f} ฿")
        
        if 'property_type' in search_params:
            suggestions.append("• Рассмотреть другие типы недвижимости")
        
        if 'district' in search_params:
            suggestions.append("• Посмотреть в соседних районах")
        
        if 'bedrooms' in search_params:
            bedrooms = search_params['bedrooms']
            if bedrooms > 1:
                suggestions.append(f"• Рассмотреть варианты с {bedrooms-1} спальнями")
        
        if not suggestions:
            suggestions = [
                "• Расширить критерии поиска",
                "• Рассмотреть альтернативные варианты",
                "• Обратиться к нашим экспертам за консультацией"
            ]
        
        response_parts.extend(suggestions)
        response_parts.append("\n📞 Или я могу связать вас с нашим экспертом для персональной консультации!")
        
        return "\n".join(response_parts)

    def save_message(self, session: ChatSession, message_type: str, content: str, 
                     metadata: Dict[str, Any] = None):
        """Сохраняет сообщение в историю чата"""
        message = ChatMessage(
            session_id=session.session_id,
            message_type=message_type,
            content=content,
            extra_data=metadata or {}
        )
        self.db.add(message)
        self.db.commit()

    def process_message(self, user_message: str, session_id: str = None) -> Tuple[str, List[Property], str]:
        """Основная функция обработки сообщения пользователя"""
        
        # Получаем или создаем сессию
        session = self.get_or_create_session(session_id)
        
        # Сохраняем сообщение пользователя
        self.save_message(session, "user", user_message)
        
        # Анализируем сообщение
        search_params = self.parse_user_message(user_message)
        
        # Ищем недвижимость
        found_properties = self.search_properties(search_params)
        
        # Генерируем ответ
        ai_response = self.generate_response(user_message, found_properties, search_params, session)
        
        # Сохраняем ответ ИИ
        self.save_message(session, "assistant", ai_response, {
            "search_params": search_params,
            "found_count": len(found_properties),
            "property_ids": [p.id for p in found_properties]
        })
        
        return ai_response, found_properties, session.session_id
