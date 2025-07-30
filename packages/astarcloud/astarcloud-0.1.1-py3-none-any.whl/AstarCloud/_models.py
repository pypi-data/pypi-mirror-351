from pydantic import BaseModel


class Message(BaseModel):
    role: str
    content: str


class CompletionRequest(BaseModel):
    model: str
    messages: list[Message]
    stream: bool = False


class CompletionChoice(BaseModel):
    index: int
    message: Message
    finish_reason: str | None = None


class CompletionResponse(BaseModel):
    id: str
    created: int
    model: str
    choices: list[CompletionChoice]
