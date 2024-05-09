import uuid
from os import access
import select
from fastapi.params import Header
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest
from sqlalchemy import select, update, delete, Result
from src.models.user_model import User


async def test_get_user_messages(ac: AsyncClient):
    pass


async def test_create_message(ac: AsyncClient):
    pass


async def test_delete_message(ac: AsyncClient):
    pass


async def test_edit_message(ac: AsyncClient):
    pass


async def get_messages_from_conv(ac: AsyncClient):
    pass
