from unittest.mock import patch


def valid_payload():
    return {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "subject": "Hello",
        "message": "This is a valid message."
    }


def test_contact_success(client):
    response = client.post("/contact", json=valid_payload())
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_contact_invalid(client):
    response = client.post("/contact", json={
        "name": "J",
        "email": "bad",
        "subject": "Hi",
        "message": "short"
    })
    assert response.status_code == 422


def test_contact_rate_limited(client):
    payload = valid_payload()

    for _ in range(11):
        response = client.post("/contact", json=payload)

    assert response.status_code == 429


@patch("contact_responder.api.routes.send_autoresponse")
def test_valid_triggers_email(mock_send, client):
    response = client.post("/contact", json=valid_payload())

    assert response.status_code == 200
    assert response.json()["is_spam"] is False
    mock_send.assert_called_once()


@patch("contact_responder.api.routes.send_autoresponse")
def test_spam_does_not_send(mock_send, client):
    spam_payload = valid_payload()
    spam_payload["message"] = "buy now buy now buy now buy now buy now buy now"

    response = client.post("/contact", json=spam_payload)

    assert response.status_code == 200
    if response.json()["is_spam"]:
        mock_send.assert_not_called()


