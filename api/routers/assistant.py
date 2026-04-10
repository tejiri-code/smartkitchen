import base64
from io import BytesIO
from PIL import Image
from fastapi import APIRouter

from api.dependencies import (
    get_query_assistant,
    ensure_ollama_available,
    get_joint_embedder,
    get_recipe_engine,
    get_rl_reranker,
)
from api.schemas.assistant import AskRequest, AskResponse
from utils.rag_retriever import RAGRetriever

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask_assistant(body: AskRequest):
    assistant = get_query_assistant()

    if body.use_ollama:
        ensure_ollama_available()

    history = [{"question": t.question, "answer": t.answer} for t in body.history[-3:]]

    # RAG: Retrieve relevant recipes per question, with RL reranking
    embedder = get_joint_embedder()
    engine = get_recipe_engine()
    reranker = get_rl_reranker()
    context = RAGRetriever.retrieve(
        body.question, body.context, embedder, engine, reranker=reranker
    )

    if body.image:
        try:
            # Decode base64 image
            image_data = base64.b64decode(body.image.split(",")[-1])
            image = Image.open(BytesIO(image_data))

            # Use multimodal answer
            answer = assistant.answer_with_image(
                question=body.question,
                image=image,
                context=context,
                history=history,
            )
        except Exception as e:
            answer = f"Error processing image: {e}"
    else:
        answer = assistant.answer_with_history(
            question=body.question,
            context=context,
            history=history,
        )

    return AskResponse(answer=answer, used_model=assistant.is_loaded, context=context)
