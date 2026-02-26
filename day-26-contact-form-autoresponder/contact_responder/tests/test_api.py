from fastapi.testclient import TestClient
from fastapi import FastAPI

from contact_responder.api.routes import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)


def test_contact_success():
    response = client.post("/contact", json={
        "name": "Jane Doe",
        "email": "jane@example.com",
        "subject": "Hello",
        "message": "This is a valid message."
    })

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_contact_invalid():
    response = client.post("/contact", json={
        "name": "J",
        "email": "bad",
        "subject": "Hi",
        "message": "short"
    })

    assert response.status_code == 400