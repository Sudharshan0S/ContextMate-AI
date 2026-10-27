from pydantic import BaseModel, Field, field_validator

from app.config import MAX_MESSAGE_LENGTH


class ChatRequest(BaseModel):
    conversation_id: str = Field(
        min_length=1,
        max_length=100,
    )
    message: str = Field(
        min_length=1,
        max_length=MAX_MESSAGE_LENGTH,
    )

    @field_validator("conversation_id", "message")
    @classmethod
    def strip_strings(cls, value: str) -> str:
        return value.strip()


class ChatResponse(BaseModel):
    conversation_id: str
    response: str


class MessageItem(BaseModel):
    role: str
    content: str


class HistoryResponse(BaseModel):
    conversation_id: str
    messages: list[MessageItem]