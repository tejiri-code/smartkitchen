import io
from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from PIL import Image

from api.dependencies import get_ingredient_model, get_recipe_engine
from api.schemas.ingredients import IngredientResponse, IngredientRecommendResponse
from api.schemas.recipes import RecipeWithScore
from utils.retrieval import ContextRetriever

router = APIRouter()


def _load_image(file: UploadFile) -> Image.Image:
    contents = file.file.read()
    try:
        return Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=422, detail="Could not read image file.")


@router.post("/ingredients", response_model=IngredientResponse)
async def classify_ingredients(
    file: UploadFile = File(...),
    threshold: float = Query(default=0.5, ge=0.1, le=0.9),
    include_all: bool = Query(default=False),
):
    image = _load_image(file)
    model = get_ingredient_model()

    detected = model.predict(image, threshold=threshold)
    all_probs = model.predict_all(image) if include_all else None

    return IngredientResponse(
        detected=detected,
        all_probabilities=all_probs,
        count=len(detected),
    )


@router.post("/ingredients/with-recipes", response_model=IngredientRecommendResponse)
async def classify_ingredients_with_recipes(
    file: UploadFile = File(...),
    threshold: float = Query(default=0.5, ge=0.1, le=0.9),
    top_k: int = Query(default=3, ge=1, le=10),
):
    image = _load_image(file)
    model = get_ingredient_model()
    engine = get_recipe_engine()

    detected = model.predict(image, threshold=threshold)
    available = list(detected.keys())

    if available:
        top_ingredient = max(detected.items(), key=lambda x: x[1])[0]
        query_ingredients = [top_ingredient]
    else:
        query_ingredients = []

    raw_recs = engine.recommend_by_ingredients(query_ingredients, top_k=top_k) if query_ingredients else []
    recommendations = [RecipeWithScore(**r) for r in raw_recs]

    missing_all: list[str] = []
    subs_all: list[dict] = []
    if raw_recs:
        missing_all = raw_recs[0].get("missing_ingredients", [])
        subs_all = engine.get_all_substitutions_for_missing(missing_all)

    context = ContextRetriever.build_context(
        ingredients=available,
        recipes=raw_recs,
        missing_ingredients=missing_all,
        substitutions=subs_all,
    )

    return IngredientRecommendResponse(
        detected=detected,
        count=len(detected),
        recommendations=recommendations,
        context=context,
    )
