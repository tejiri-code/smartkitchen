from fastapi import APIRouter

from api.dependencies import get_query_assistant, ensure_ollama_available
from api.schemas.assistant import AskRequest, AskResponse

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask_assistant(body: AskRequest):
    assistant = get_query_assistant()

    if body.use_ollama:
        ensure_ollama_available()

    history = [{"question": t.question, "answer": t.answer} for t in body.history[-3:]]

    answer = assistant.answer_with_history(
        question=body.question,
        context=body.context,
        history=history,
    )

    return AskResponse(answer=answer, used_model=assistant.is_loaded)
