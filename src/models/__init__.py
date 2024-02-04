__all__ = (
    'Base',
    'db_handler',
    'DatabaseHandler'
    )
from .base import db_handler, DatabaseHandler
# Я знаю, что внизу какая-то жопа, но я не знаю как это фиксить
from .chat_models import Base
from .user_model import Base