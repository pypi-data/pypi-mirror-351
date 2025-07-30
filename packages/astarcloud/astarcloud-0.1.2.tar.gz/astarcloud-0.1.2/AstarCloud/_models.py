from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Message(BaseModel):
    role: str
    content: str
    images: Optional[list] = None
    tool_calls: Optional[list] = None


class CompletionRequest(BaseModel):
    model: str
    messages: list[Message]
    stream: bool = False


class CompletionChoice(BaseModel):
    index: int
    message: Message
    finish_reason: str | None = None


class CompletionResponse(BaseModel):
    model: str
    created_at: datetime
    done: bool
    done_reason: Optional[str] = None
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None
    message: Message
