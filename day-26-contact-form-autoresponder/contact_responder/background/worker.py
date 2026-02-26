from contact_responder.background.email_job import send_autoresponse


def handle_result(result: dict) -> None:
    if result["status"] != "ok":
        return

    if result["is_spam"]:
        return

    send_autoresponse(result["email_context"])