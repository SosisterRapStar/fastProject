import time
from .logger import log


class ASGIMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        type = scope["type"]
        path = scope["path"]
        start = time.time()
        await self.app(scope, receive, send)
        process_time = time.time() - start

        log_dict = {"protocol": type, "path": path, "process_time": process_time}
        log.debug(log_dict)
        log.debug(scope.get("headers", []))
