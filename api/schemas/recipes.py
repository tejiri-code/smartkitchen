from typing import List, Optional
from pydantic import BaseModel


class Recipe(BaseModel):
    name: str
    ingredients: List[str]
    steps: List[str]
    prep_time: str
    cuisine: str
    category: str
    match_score: Optional[float] = None


class RecipeWithScore(Recipe):
    score: float
    matched_ingredients: List[str]
    missing_ingredients: List[str]


class RecipeByDishResponse(BaseModel):
    recipe: Optional[Recipe]


class RecommendRequest(BaseModel):
    available_ingredients: List[str]
    top_k: int = 3


class RecommendResponse(BaseModel):
    recommendations: List[RecipeWithScore]


class SubstitutionResponse(BaseModel):
    ingredient: str
    alternatives: List[str] = []
    notes: str = ""
