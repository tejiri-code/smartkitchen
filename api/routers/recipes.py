from fastapi import APIRouter, Query, HTTPException
from api.dependencies import get_recipe_engine
from api.schemas.recipes import (
    RecipeByDishResponse,
    RecommendRequest,
    RecommendResponse,
    SubstitutionResponse,
    RecipeWithScore,
)

router = APIRouter()


@router.get("/by-dish", response_model=RecipeByDishResponse)
def get_recipe_by_dish(dish: str = Query(..., description="Dish name to look up")):
    engine = get_recipe_engine()
    recipe = engine.get_recipe_by_dish(dish, threshold=0.6)
    return RecipeByDishResponse(recipe=recipe)


@router.post("/recommend", response_model=RecommendResponse)
def recommend_recipes(body: RecommendRequest):
    engine = get_recipe_engine()
    raw = engine.recommend_by_ingredients(body.available_ingredients, top_k=body.top_k)
    recs = [RecipeWithScore(**r) for r in raw]
    return RecommendResponse(recommendations=recs)


@router.get("/substitutions", response_model=SubstitutionResponse)
def get_substitutions(ingredient: str = Query(...)):
    engine = get_recipe_engine()
    result = engine.get_substitutions(ingredient)
    if result is None:
        return SubstitutionResponse(ingredient=ingredient, alternatives=[], notes="")
    return SubstitutionResponse(
        ingredient=result["ingredient"],
        alternatives=result.get("alternatives", []),
        notes=result.get("notes", ""),
    )
