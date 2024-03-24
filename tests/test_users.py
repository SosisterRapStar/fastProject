import select
from httpx import AsyncClient
import pytest
from tests.conftest import session
from sqlalchemy import select, update, delete, Result
from src.models.user_model import User


async def test_async_register(ac: AsyncClient):
    payload = {
        "name": "A2yncUser2",
        "email": "user@example.com",
        "password": "string",
        "password_repeat": "string"
    }
    response = await ac.post("/api/v1/users/register", json=payload)
    assert response.status_code == 200
    
    async with session() as ses:
        stmt = select(User).where(User.name == payload["name"])
        user = await ses.scalar(stmt)
        assert user is not None
        
    assert user.name == payload["name"]
    assert user.email == payload["email"]   
    
        
    
    


    