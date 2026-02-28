import uuid
from contextlib import contextmanager


class CorrelationContext:
    """Explicit correlation context passed to functions, no global state."""
    def __init__(self, correlation_id: str | None = None):
        self.correlation_id = correlation_id or str(uuid.uuid4())

    @contextmanager
    def use(self):
        yield self.correlation_id