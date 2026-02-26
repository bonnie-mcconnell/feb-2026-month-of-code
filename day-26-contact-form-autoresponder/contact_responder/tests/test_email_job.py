import logging
from contact_responder.background.email_job import send_autoresponse


def test_send_autoresponse_runs(caplog):
    caplog.set_level(logging.INFO)

    context = {"email": "test@example.com"}
    send_autoresponse(context)

    assert "Sending autoresponse to test@example.com" in caplog.text