try:
    from backend.models.property import Property
    from backend.models.property_image import PropertyImage
    from backend.models.project import Project
    from backend.models.favorite import Favorite
    from backend.models.user import User
    from backend.models.chat import ChatSession, ChatMessage
except ImportError:
    from models.property import Property
    from models.property_image import PropertyImage
    from models.project import Project
    from models.favorite import Favorite
    from models.user import User
    from models.chat import ChatSession, ChatMessage

__all__ = ["Property", "PropertyImage", "Project", "Favorite", "User", "ChatSession", "ChatMessage"]