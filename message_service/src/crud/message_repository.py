from src.crud.repo_abstract import CRUDAlchemyRepository
from src.models.chat_models import Message


class MessageRepository(CRUDAlchemyRepository):
    _model = Message
