"""Feedback endpoints for recipe and chat ratings."""

import json
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter

from api.schemas.feedback import RecipeFeedback, ChatFeedback

router = APIRouter()

FEEDBACK_FILE = Path("data/feedback.jsonl")


@router.post("/recipe")
def submit_recipe_feedback(feedback: RecipeFeedback):
    """Record user feedback on a recipe."""
    # Ensure data directory exists
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Append feedback as newline-delimited JSON
    entry = {
        "type": "recipe",
        "timestamp": datetime.utcnow().isoformat(),
        "recipe_name": feedback.recipe_name,
        "rating": feedback.rating,
    }

    with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    return {"status": "recorded", "recipe": feedback.recipe_name, "rating": feedback.rating}


@router.post("/chat")
def submit_chat_feedback(feedback: ChatFeedback):
    """Record user feedback on an assistant response."""
    # Ensure data directory exists
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Append feedback as newline-delimited JSON
    entry = {
        "type": "chat",
        "timestamp": datetime.utcnow().isoformat(),
        "question": feedback.question,
        "answer": feedback.answer,
        "helpful": feedback.helpful,
    }

    with open(FEEDBACK_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    return {"status": "recorded", "helpful": feedback.helpful}
