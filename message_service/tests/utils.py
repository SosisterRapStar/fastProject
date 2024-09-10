from src.crud.repo_abstract import CRUDAlchemyRepository
from src.models.chat_models import UserConversationSecondary
from src.schemas.users import User_on_response, UserInDB

import uuid


class TestFullUser(UserInDB):
    id: uuid.UUID

def create_auth_form(model: TestFullUser) -> dict:

    auth_form = {
        "username": model.name,
        "password": model.password,
    }
    return auth_form


async def mock_conv_add(
        self,
        current_user_id: uuid.UUID,
        user_id: uuid.UUID,
        conv_id: uuid.UUID,
        permission: bool,
    ) -> None:


        
        new_asoc = UserConversationSecondary(edit_permission=permission)
        new_asoc.conversation_id = conv_id
        new_asoc.user_id = user_id
        self._session.add(new_asoc)
        await self._session.commit()


        
def validate_detail_error_response_field(expected_error_message, schema: dict):
    assert schema['detail']
    assert schema['detail'] == expected_error_message

def validate_user_response_schema(schema: dict):
    try:
        User_on_response(**schema)
    except ValueError as e:
        assert False, f"Response JSON is not valid (not User_on_response): {e}"
        
        
async def mock_get_permissions(self, current_user_id: uuid.UUID, conv_id: uuid.UUID):
    pass