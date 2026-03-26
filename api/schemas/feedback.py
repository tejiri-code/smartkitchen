"""Feedback schemas for recipe and chat ratings."""

from pydantic import BaseModel


class RecipeFeedback(BaseModel):
    """User rating for a recipe."""

    recipe_name: str
    rating: int  # 1 = helpful/like, -1 = not helpful/dislike


class ChatFeedback(BaseModel):
    """User rating for an AI assistant response."""

    question: str
    answer: str
    helpful: bool  # True = helpful, False = not helpful
