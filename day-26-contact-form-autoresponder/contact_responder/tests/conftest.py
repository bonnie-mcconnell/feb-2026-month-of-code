import pytest
from fastapi.testclient import TestClient
from contact_responder.bootstrap import create_app


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)