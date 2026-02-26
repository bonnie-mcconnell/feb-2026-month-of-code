from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from contact_responder.api.schemas import ContactRequest, ContactResponse
from contact_responder.background.email_job import send_autoresponse
from contact_responder.services.responder_service import ResponderService

def create_router(service: ResponderService) -> APIRouter:
    router = APIRouter()

    @router.post("/contact", response_model=ContactResponse)
    def submit_contact(
        payload: ContactRequest,
        request: Request,
        background_tasks: BackgroundTasks,
    ):
        data = payload.model_dump()

        if not data.get("source_ip"):
            data["source_ip"] = request.client.host if request.client else "0.0.0.0"

        result = service.process(data)

        if result["status"] == "invalid":
            raise HTTPException(status_code=400, detail=result)

        if result["status"] == "rate_limited":
            raise HTTPException(status_code=429, detail=result)

        if result["status"] == "ok" and not result["is_spam"]:
            background_tasks.add_task(
                send_autoresponse,
                result["email_context"]
            )

        return ContactResponse(
            status=result["status"],
            message_id=result["message_id"],
            spam_score=result["spam_score"],
            is_spam=result["is_spam"],
        )

    return router