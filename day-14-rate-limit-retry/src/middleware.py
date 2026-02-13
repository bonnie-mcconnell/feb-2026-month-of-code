class Middleware:
    """
    Base middleware interface.

    Subclasses should override __call__ and return a wrapped function.
    """

    def __call__(self, request_fn):
        return request_fn
