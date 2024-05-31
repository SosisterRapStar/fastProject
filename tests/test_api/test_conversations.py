import uuid
from httpx import AsyncClient
import pytest
from src.models.chat_models import Conversation
from src.models.user_model import User
from sqlalchemy import select
from src.schemas.conversation import ConversationResponse
from models.utils import mock_conv_add, validate_detail_error_response_field, mock_get_permissions, validate_user_response_schema


def validate_conversation_response_schema(schema: dict):
    try:
        ConversationResponse(**schema)
    except ValueError as e:
        assert False, f"Response JSON is not valid (not User_on_response): {e}"

async def test_create_conversation(ac: AsyncClient, function_conv_request_model, override_get_current_user_auth):
    response = await ac.post("api/v1/conversations/create/", json=function_conv_request_model.model_dump())
    exception_code = 200
    assert response.status_code == exception_code
    validate_conversation_response_schema(response.json())

async def test_delete_conversation(ac: AsyncClient, function_create_conv_for_test, override_get_current_user_auth, monkeypatch):
    monkeypatch.setattr("src.crud.conversation_repository.ConversationRepository.get_permissions", mock_get_permissions)
    response = await ac.delete(f"api/v1/conversations/{function_create_conv_for_test.id}/")
    
    
    expected_code = 200
    assert response.status_code == expected_code
    
    
async def test_get_users_in_conversation(ac: AsyncClient, function_create_conv_for_test):
    response = await ac.get(f"api/v1/conversations/users/{function_create_conv_for_test.id}/")
    expected = 200
    assert response.status_code == expected
    for user_schema in response.json():
        validate_user_response_schema(schema=user_schema    )
    


async def test_add_user_to_conversation(ac: AsyncClient, function_create_conv_for_test, function_create_add_user_schema, override_get_current_user_auth, monkeypatch):
    monkeypatch.setattr("src.crud.conversation_repository.ConversationRepository.add_user", mock_conv_add)
    response = await ac.post(f"api/v1/conversations/users/{function_create_conv_for_test.id}/", json=function_create_add_user_schema.model_dump())
    expected_code = 200
    
    assert response.status_code == expected_code
    
    
async def test_update_conversation_by_id(ac: AsyncClient, function_create_conv_for_test, function_get_update_schema, override_get_current_user_auth, monkeypatch):
    monkeypatch.setattr("src.crud.conversation_repository.ConversationRepository.get_permissions", mock_get_permissions)
    response = await ac.patch(f"api/v1/conversations/?id={function_create_conv_for_test.id}", json=function_get_update_schema.model_dump())
    expected_code = 200
    
    assert response.status_code == expected_code
    validate_conversation_response_schema(response.json())

async def test_update_conversation_by_name(ac: AsyncClient, function_create_conv_for_test, function_get_update_schema, override_get_current_user_auth, monkeypatch):
    monkeypatch.setattr("src.crud.conversation_repository.ConversationRepository.get_permissions", mock_get_permissions)
    response = await ac.patch(f"api/v1/conversations/?name={function_create_conv_for_test.name}", json=function_get_update_schema.model_dump())
    expected_code = 200
    
    assert response.status_code == expected_code
    validate_conversation_response_schema(response.json())
    
    
async def test_get_conv_by_name(ac: AsyncClient, function_create_conv_for_test, override_get_current_user_auth):

    response = await ac.get(f"api/v1/conversations/?id={function_create_conv_for_test.id}")
    expected_code = 200
    
    assert response.status_code == expected_code
    validate_conversation_response_schema(response.json())
    
async def test_conv_by_id(ac: AsyncClient, function_create_conv_for_test, override_get_current_user_auth):

    response = await ac.get(f"api/v1/conversations/?name={function_create_conv_for_test.name}")
    expected_code = 200
    
    assert response.status_code == expected_code
    validate_conversation_response_schema(response.json())
    
async def test_get_all_convs(ac: AsyncClient, function_create_conv_for_test, override_get_current_user_auth):

    response = await ac.get(f"api/v1/conversations/")
    expected_code = 200
    
    assert response.status_code == expected_code
    assert isinstance(response.json(), list)
    for i in response.json():
        validate_conversation_response_schema(i)
        
        
async def test_create_non_auth_conversation(ac: AsyncClient, function_conv_request_model):
    response = await ac.post("api/v1/conversations/create/", json=function_conv_request_model.model_dump())
    exception_code = 401
    assert response.status_code == exception_code
    validate_detail_error_response_field("You are not authorized", response.json())
    

        
async def test_non_auth_add_user_to_conversation(ac: AsyncClient, function_create_conv_for_test, function_create_add_user_schema):
    
    response = await ac.post(f"api/v1/conversations/users/{function_create_conv_for_test.id}/", json=function_create_add_user_schema.model_dump())
    expected_code = 401
    
    assert response.status_code == expected_code
    validate_detail_error_response_field("You are not authorized", response.json())


async def test_non_auth_add_user_to_conversation(ac: AsyncClient, function_create_conv_for_test, function_create_add_user_schema):
    
    response = await ac.post(f"api/v1/conversations/users/{function_create_conv_for_test.id}/", json=function_create_add_user_schema.model_dump())
    expected_code = 401
    
    assert response.status_code == expected_code
    validate_detail_error_response_field("You are not authorized", response.json())
    

async def test_non_auth_update_conversation_by_id(ac: AsyncClient, function_create_conv_for_test, function_get_update_schema):
    
    response = await ac.patch(f"api/v1/conversations/?id={function_create_conv_for_test.id}", json=function_get_update_schema.model_dump())
    expected_code = 401
    
    assert response.status_code == expected_code
    validate_detail_error_response_field("You are not authorized", response.json())

async def test_non_auth_update_conversation_by_name(ac: AsyncClient, function_create_conv_for_test, function_get_update_schema):
    
    response = await ac.patch(f"api/v1/conversations/?name={function_create_conv_for_test.name}", json=function_get_update_schema.model_dump())
    expected_code = 401
    
    assert response.status_code == expected_code
    validate_detail_error_response_field("You are not authorized", response.json())
    
    
async def test_non_permission_update_conversation_by_id(ac: AsyncClient, function_create_conv_for_test, function_get_update_schema, override_get_current_user_auth):
    
    response = await ac.patch(f"api/v1/conversations/?id={function_create_conv_for_test.id}", json=function_get_update_schema.model_dump())
    expected_code = 403
    
    assert response.status_code == expected_code
    validate_detail_error_response_field("User has no edit permissions", response.json())

async def test_non_permission_update_conversation_by_name(ac: AsyncClient, function_create_conv_for_test, function_get_update_schema, override_get_current_user_auth):
    
    response = await ac.patch(f"api/v1/conversations/?name={function_create_conv_for_test.name}", json=function_get_update_schema.model_dump())
    expected_code = 403
    
    assert response.status_code == expected_code
    validate_detail_error_response_field("User has no edit permissions", response.json())
    
async def test_add_user_to_conversation(ac: AsyncClient, function_create_conv_for_test, function_create_add_user_schema, override_get_current_user_auth):
    response = await ac.post(f"api/v1/conversations/users/{function_create_conv_for_test.id}/", json=function_create_add_user_schema.model_dump())
    expected_code = 403
    
    assert response.status_code == expected_code
    validate_detail_error_response_field("User has no edit permissions", response.json())
    
    

# async def test_delete_user_from_conversation(ac: AsyncClient):
#     response = await ac.post("")
#     pass


# async def test_update_conversation(ac: AsyncClient):
#     response = await ac.update("")
#     pass


# async def test_get_users_in_conversation(ac: AsyncClient):
#     response = await ac.get("")
#     pass