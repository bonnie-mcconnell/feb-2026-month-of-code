class Middleware:
    """
    Base middleware interface.

    Subclasses should override __call__ and return a wrapped function.
    Provides optional hook for observability/logging.
    """

    name: str = "middleware"

    def __call__(self, request_fn):
        return request_fn
