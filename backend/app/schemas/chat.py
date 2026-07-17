from pydantic import BaseModel

class ChatRequest(BaseModel):
    session_id: int
    message: str

class ChatResponse(BaseModel):
    reply: str
