from pydantic import BaseModel, Field


class ContactRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str
    subject: str = Field(min_length=3, max_length=150)
    message: str = Field(min_length=10, max_length=5000)
    source_ip: str | None = None


class ContactResponse(BaseModel):
    status: str
    message_id: str | None = None
    spam_score: int | None = None
    is_spam: bool | None = None