from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from api.schemas.recipes import RecipeWithScore


class IngredientResponse(BaseModel):
    detected: Dict[str, float]
    all_probabilities: Optional[Dict[str, float]] = None
    count: int


class IngredientRecommendResponse(IngredientResponse):
    recommendations: List[RecipeWithScore]
    context: Dict[str, Any] = {}
