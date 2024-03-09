from jose import JWTError
from starlette.responses import Response
import time
from .logger import log
from src.authorization.security import get_token_payload
from starlette.datastructures import Headers


class WebSocketAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        request_type = scope["type"]
        path = scope["path"]
        if request_type == "websocket":
            headers = Headers(scope=scope)
            auth = headers.get("Authorization", None)
            if not auth:
                log.error(
                    f"{request_type} Protocol: {path} No Authorization in headers"
                )
                await send({"type": "websocket.close", "code": 401})
                return

            token_type, token = auth.split()

            if token_type != "Bearer":
                log.error(f"{request_type} Protocol: {path} No Bearer token type")
                # scope['headers'].update("WWW-Authenticate", "Bearer")
                await send({"type": "websocket.close", "code": 401})
                return
            try:
                payload = get_token_payload(token)
                user_id = payload["id"]
            except (LookupError, JWTError):
                log.error(
                    f"{request_type} Protocol: {path} Websocket: Non authorized user"
                )
                await send({"type": "websocket.close", "code": 401})
                return

            log.debug(f"Request for curr user id")
            scope["user_id"] = user_id
            await self.app(scope, receive, send)
            del scope["user_id"]
        else:
            await self.app(scope, receive, send)
