from fastapi import HTTPException


class PasswordVerificationError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f"{self.message}"
        return f"Wrong user credentials"


class InvalidTokenError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidRefreshTokenError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserCredentialsError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=401,
            detail="Wrong user credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class NonAuthorizedError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=401,
            detail="You are not authorized",
            headers={"WWW-Authenticate": "Bearer"},
        )
