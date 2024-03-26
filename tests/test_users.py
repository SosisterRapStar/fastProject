import uuid
from os import access
import select
from fastapi.params import Header
from httpx import AsyncClient
import pytest
from tests.conftest import session
from sqlalchemy import select, update, delete, Result
from src.models.user_model import User




class TestUser:
    user_name: str
    user_email: str
    user_password: str
    user_token: str
    user_id: uuid.UUID
    
    
class NoExistTestUser:
    user_name: str = "NotExist"
    user_email: str = "thereisnoemail@com.com"
    user_password: str = "very_bad_password"
    


async def test_async_register(ac: AsyncClient):
    given_payload = {
        "name": "test_user", 
        "email": "testemail@user.com",
        "password": "test_password",
        "password_repeat": "test_password"
    }
    
    TestUser.user_name = given_payload["name"]
    TestUser.user_email = given_payload["email"]
    TestUser.user_password = given_payload["password"]
    
    response = await ac.post("/api/v1/users/register", json=given_payload)
    
    expected_code = 200
    
    assert response.status_code == expected_code
    
async def test_get_registered_user_from_db(ac: AsyncClient):
    
    async with session() as ses:
        stmt = select(User).where(User.name == TestUser.user_name)
        user = await ses.scalar(stmt)
        assert user is not None
        TestUser.user_id = user.id
        
    assert user.email == TestUser.user_email
    print(user.name)
    

async def test_correct_async_auth(ac: AsyncClient):
    given_form_data = {
            'username': TestUser.user_name,
            'password': TestUser.user_password,
        }
    
    response = await ac.post("api/v1/auth/token", file=given_form_data) 
    
    expected_code = 200
    
    assert response.status_code == expected_code
    
    TestUser.user_token = response.json()['access_token']
    
    
async def test_correct_async_auth(ac: AsyncClient):
    given_form_data = {
            'username': TestUser.user_name,
            'password': "Not user password",
        }
    
    response = await ac.post("api/v1/auth/token", file=given_form_data) 
    
    expected_code = 401
    
    assert response.status_code == expected_code
    assert response.json()['details'] == "Wrong user credentials"
    
    
    
   

async def test_real_get_user_me(ac: AsyncClient):
    
    headers = {'Authorization': 'Bearer ' + TestUser.user_token}
    
    response = await ac.get("api/v1/users/me",  headers=headers) 
    
    expected_code = 200
    
    assert response.status_code == expected_code

async def test_inc_real_get_user_me(ac: AsyncClient):
    
    headers = {'Authorization': 'NotBearer ' + TestUser.user_token}
    
    response = await ac.get("api/v1/users/me",  headers=headers) 
    
    expected_code = 401
    
    assert response.status_code == expected_code
    assert response.json()['details'] == "You are not authorized"
    
    response = await ac.get("api/v1/users/me")
    
    expected_code = 401
    
    assert response.status_code == expected_code
    assert response.json()['details'] == "You are not authorized"
    
    headers = {'Authorization': 'Bearer ' + 'InvalidToken'}
    response = await ac.get("api/v1/users/me",  headers=headers) 
    
    assert response.status_code == expected_code
    assert response.json()['details'] == "Invalid token"
    
    
async def test_get_user_convs_user(ac: AsyncClient):
    headers = {'Authorization': 'Bearer ' + TestUser.user_token}
    response = await ac.get("api/v1/users/convs",  headers=headers)
    expected_code = 200
    assert response.status_code == expected_code
    
    
    
async def test_delete_user(ac: AsyncClient):
    
    async with session() as ses:
        stmt = select(User).where(User.id == TestUser.user_id)
        result = await ses.scalar(stmt)
    assert result is not None
    
    response = await ac.delete("api/v1/users/" + TestUser.user_id + "/")
    expected_code = 200
    assert response.status_code == expected_code
    
    async with session() as ses:
        stmt = select(User).where(User.id == TestUser.user_id)
        result = await ses.scalar(stmt)
    assert result is None
    
    
        
    
    


    