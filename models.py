from enum import Enum

from pydantic import BaseModel


class ResponseChatMessage(BaseModel):
    role: str
    content: str
    images: None = None


class ResponseChunk(BaseModel):
    done: bool
    created_at: str
    model: str
    message: ResponseChatMessage


class ResponseDoneChunk(ResponseChunk):
    context: list[str] | None = None
    total_duration: int
    prompt_eval_duration: int
    eval_count: int
    eval_duration: int


class ChatPreference(Enum): ...


class ChatUserInformation(BaseModel):
    full_name: str


class ChatData(BaseModel):
    messages: list[dict[str, str]]
    preferences: list[ChatPreference]
