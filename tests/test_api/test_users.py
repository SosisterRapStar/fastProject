
import uuid

from requests import session

from fastapi.params import Header
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest
from sqlalchemy import select, update, delete, Result
from src.models.user_model import User
from src.schemas.users import CreateUser, User_on_response, UserInDB
from src.schemas.token_schema import TokenResponse
from pydantic import BaseModel
from src.crud.user_repository import UserRepository
from models.utils import create_auth_form, validate_detail_error_response_field, validate_user_response_schema
from auth_mocks import mock_get_token
from src.schemas.conversation import ConversationResponse
import data_generator




    
async def test_registration(ac: AsyncClient, function_get_env_for_registration: CreateUser):
    response = await ac.post("api/v1/users/register", json=function_get_env_for_registration.model_dump())
    expected_code = 200
    
    assert response.status_code == expected_code
    

async def test_authorization(ac: AsyncClient, function_create_user_for_test, monkeypatch):
    
    
    model = function_create_user_for_test
    auth_form = create_auth_form(model)

    
    monkeypatch.setattr("src.authorization.services.JWTService.get_token", mock_get_token)
    
    response = await ac.post("api/v1/auth/token", data=auth_form)
    
    expected_code = 200
    
    assert response.status_code == expected_code
    try:
        TokenResponse(**response.json())
    except ValueError as e:
        assert False, f"Response JSON is not valid (not TokenResponse): {e}"
        
async def test_get_user_by_name(ac: AsyncClient, function_create_user_for_test):
    response = await ac.get(f"api/v1/users/?name={function_create_user_for_test.name}")
    
    expected_code = 200
     
    assert response.status_code == expected_code
    validate_user_response_schema(response.json())
    
        
async def test_get_user_by_id(ac: AsyncClient, function_create_user_for_test):
    response = await ac.get(f"api/v1/users/?id={function_create_user_for_test.id}")
    
    expected_code = 200
    
    assert response.status_code == expected_code
    validate_user_response_schema(response.json())


async def test_get_all_users(ac: AsyncClient, function_fill_db_for_many_users):
    response = await ac.get("api/v1/users/")
    
    expected_code = 200
    assert response.status_code == expected_code
    assert isinstance(response.json(), list)
    for schema in response.json():
        validate_user_response_schema(schema)
        
   
async def test_delete_user(ac: AsyncClient, function_create_user_for_test):
    model = function_create_user_for_test
    response = await ac.delete(f"api/v1/users/{model.id}/")
    expected_code = 200
    
    assert response.status_code == expected_code
    assert response.json()['id'] == str(model.id)
    
    
async def test_user_get_me(ac: AsyncClient, override_get_current_user_auth):
    response = await ac.get(f"api/v1/users/me")
    expected_code = 200
    
    assert response.status_code == expected_code
    validate_user_response_schema(response.json())
        
async def test_get_auth_user_convs(ac: AsyncClient, override_get_current_user_auth):
    response = await ac.get(f"api/v1/users/convs/")
    expected_code = 200
    
    assert response.status_code == expected_code
    for schema in response.json():
        try:
            ConversationResponse(**schema)
        except ValueError as e:
            assert False, f"Response JSON is not valid (not User_on_response): {e}"
        
async def test_get_user_messages(ac: AsyncClient, override_get_current_user_auth):
    response = await ac.get("api/v1/messages/my")
    assert response.status_code == 200
        


async def test_update_user(ac: AsyncClient, function_update_shchema, override_get_current_user_auth):
    response = await ac.patch("api/v1/users/me", json=function_update_shchema.model_dump())
    expected_code = 200
    assert response.status_code == expected_code
    validate_user_response_schema(response.json())

    
#---------------------------------------------------------

    

# async def test_negative_get_all_users(ac: AsyncClient):
#     response = await ac.get("api/v1/users/")
#     expected_code = 200
#     assert response.status_code == expected_code
#     assert response.json() == []
    

async def test_negative_get_user_by_name(ac: AsyncClient):
    response = await ac.get(f"api/v1/users/?name={data_generator.get_random_word()}")
    expected_code = 404
    
    assert response.status_code == expected_code
    validate_detail_error_response_field("User not found", response.json())
    
async def test_negative_get_user_by_id(ac: AsyncClient):
    response = await ac.get(f"api/v1/users/?id={uuid.uuid4()}")
    expected_code = 404
    
    assert response.status_code == expected_code
    validate_detail_error_response_field("User not found", response.json())
    
async def test_non_valid_uuid(ac: AsyncClient):
    response = await ac.get(f"api/v1/users/?id={data_generator.get_random_word()}")
    expected_code = 422
    
    assert response.status_code == expected_code
    
    
async def test_non_authorized_user(ac: AsyncClient):
    response = await ac.get("api/v1/users/me")
    
    expected_code = 401
    
    assert response.status_code == expected_code
    validate_detail_error_response_field("You are not authorized", response.json())
    
async def test_wrong_headers(ac: AsyncClient):
    headers = {"Authorization": data_generator.get_random_word()}
    
    response = await ac.get("api/v1/users/me", headers=headers)
    expected_code = 401
    
    assert response.status_code == expected_code
    validate_detail_error_response_field("Invalid token", response.json())
    
async def test_no_jwt(ac: AsyncClient):
    response = await ac.get("api/v1/users/me")
    headers = {"Authorization": f"Bearer {data_generator.get_random_word()}"}
    expected_code = 401
    
    assert response.status_code == expected_code
    validate_detail_error_response_field("You are not authorized", response.json())

async def test__non_auth_get_user_convs(ac: AsyncClient):
    response = await ac.get(f"api/v1/users/convs/")
    expected_code = 401
        
    assert response.status_code == expected_code
    validate_detail_error_response_field("You are not authorized", response.json())
        
async def test__non_auth_get_user_messages(ac: AsyncClient):
    response = await ac.get("api/v1/messages/my")
    expected_code = 401
    
    assert response.status_code == expected_code
    validate_detail_error_response_field("You are not authorized", response.json())
        


async def test_non_auth_update_user(ac: AsyncClient, function_update_shchema):
    response = await ac.patch("api/v1/users/me", json=function_update_shchema.model_dump())
    expected_code = 401
    
    assert response.status_code == expected_code
    validate_detail_error_response_field("You are not authorized", response.json())

async def test_lift_yourself_up_on_your_feet():
    poop = ''' Poopy-di scoop
            Scoop-diddy-whoop
            Whoop-di-scoop-di-poop
            Poop-di-scoopty
            Scoopty-whoop
            Whoopity-scoop, whoop-poop
            Poop-diddy, whoop-scoop
            Poop, poop
            Scoop-diddy-whoop
            Whoop-diddy-scoop
            Whoop-diddy-scoop, poop '''
            
            

    
    