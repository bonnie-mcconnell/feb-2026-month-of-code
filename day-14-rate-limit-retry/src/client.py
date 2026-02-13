from typing import Callable, List, Optional

from .middleware import Middleware


class HttpClient:
    def __init__(self, middlewares: Optional[List[Middleware]] = None):
        self.middlewares = middlewares or []

    def execute(self, request_fn: Callable):
        wrapped = request_fn

        # apply in reverse order so first middleware wraps outermost
        for middleware in reversed(self.middlewares):
            wrapped = middleware(wrapped)

        return wrapped()
