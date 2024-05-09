from fastapi import APIRouter, HTTPException


class AdminUserNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Admin user not found")


class ConversationNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Conversation not found")


class UserAlreadyAddedError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=404, detail="User already added or some of id not found"
        )


class UserNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="User not found")


class EditPermissionsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="User has no edit permissions")
