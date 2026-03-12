from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ChatTurn(BaseModel):
    question: str
    answer: str


class AskRequest(BaseModel):
    question: str
    context: Dict[str, Any] = {}
    history: List[ChatTurn] = []
    use_ollama: bool = False


class AskResponse(BaseModel):
    answer: str
    used_model: bool
