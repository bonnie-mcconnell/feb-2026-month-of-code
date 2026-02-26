from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import patch

from contact_responder.bootstrap import create_app

app = create_app()
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

    assert response.status_code == 422


def test_contact_rate_limited(client):
    payload = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "subject": "Hello",
        "message": "Valid message",
    }

    # hit more times than limit
    for _ in range(10):
        response = client.post("/contact", json=payload)

    assert response.status_code == 429


@patch("contact_responder.api.routes.send_autoresponse")
def test_spam_does_not_send(mock_send, client):
    response = client.post("/contact", json={
        "name": "Jane",
        "email": "jane@example.com",
        "subject": "Hello",
        "message": "buy now buy now buy now"
    })

    assert response.status_code == 200
    assert response.json()["is_spam"] is True
    mock_send.assert_not_called()


@patch("contact_responder.api.routes.send_autoresponse")
def test_valid_triggers_email(mock_send, client):
    response = client.post("/contact", json={
        "name": "Jane",
        "email": "jane@example.com",
        "subject": "Hello",
        "message": "This is a valid message."
    })

    assert response.status_code == 200
    mock_send.assert_called_once()