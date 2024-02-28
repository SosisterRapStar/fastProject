from datetime import timedelta, datetime
from jose import jwt, JWTError
from passlib.context import CryptContext
from src.config import security_settings



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def create_access_token(data, expire: timedelta):
    payload = data.copy()
    expire_in = datetime.utcnow() + expire
    payload.update({"iat": datetime.utcnow(), "exp": expire_in})
    token = jwt.encode(
        payload,
        security_settings.JWT_SECRET,
        algorithm=security_settings.JWT_ALGORITHM,
    )
    return token


async def create_refresh_token(data):
    return jwt.encode(
        data,
        security_settings.JWT_SECRET,
        algorithm=security_settings.JWT_ALGORITHM,
    )


def get_token_payload(token: str) -> dict:
    payload = jwt.decode(
        token,
        security_settings.JWT_SECRET,
        algorithms=security_settings.JWT_ALGORITHM,
    )

    return payload

