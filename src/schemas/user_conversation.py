from src.schemas.conversation import ConversationResponse
from src.schemas.users import User_on_response


class UserOnResponseWithConvs(User_on_response):
    conversations: list["ConversationResponse"]


class ConversationWithUsersResp(ConversationResponse):
    users: list["User_on_response"]


