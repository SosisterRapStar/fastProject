
import time
from .logger import log


class ASGIMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        start = time.time()
        await self.app(scope, receive, send)
        process_time = time.time() - start
        log_dict = {
            "url": scope['path'],
            "process_time": process_time
        }
        log.debug(log_dict)
