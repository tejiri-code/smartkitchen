from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from api.schemas.recipes import Recipe


class DishPrediction(BaseModel):
    label: str
    confidence: float


class DishResponse(BaseModel):
    predictions: List[DishPrediction]
    top_label: str
    top_confidence: float


class DishRecipeResponse(DishResponse):
    recipe: Optional[Recipe] = None
    context: Dict[str, Any] = {}
