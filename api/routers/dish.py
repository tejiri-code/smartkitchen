import io
from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from PIL import Image

from api.dependencies import get_dish_model, get_recipe_engine, get_joint_embedder
from api.schemas.dish import DishResponse, DishRecipeResponse, DishPrediction
from api.schemas.recipes import Recipe
from utils.retrieval import ContextRetriever

router = APIRouter()


def _load_image(file: UploadFile) -> Image.Image:
    contents = file.file.read()
    try:
        return Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=422, detail="Could not read image file.")


@router.post("/dish", response_model=DishResponse)
async def classify_dish(
    file: UploadFile = File(...),
    top_k: int = Query(default=3, ge=1, le=10),
):
    image = _load_image(file)
    model = get_dish_model()
    raw = model.predict(image, top_k=top_k)
    predictions = [DishPrediction(label=label, confidence=conf) for label, conf in raw]
    return DishResponse(
        predictions=predictions,
        top_label=predictions[0].label,
        top_confidence=predictions[0].confidence,
    )


@router.post("/dish/with-recipe", response_model=DishRecipeResponse)
async def classify_dish_with_recipe(
    file: UploadFile = File(...),
    top_k: int = Query(default=3, ge=1, le=10),
):
    image = _load_image(file)
    model = get_dish_model()
    engine = get_recipe_engine()
    embedder = get_joint_embedder()

    raw = model.predict(image, top_k=top_k)
    predictions = [DishPrediction(label=label, confidence=conf) for label, conf in raw]
    top = predictions[0]

    # Try both joint embedding and SequenceMatcher, return the better match
    recipes = []
    best_recipe = None
    best_score = 0.0

    # Try joint embedding first
    if embedder is not None:
        embedder_results = engine.find_by_joint_embedding(top.label, embedder, top_k=1)
        if embedder_results:
            recipe_dict = embedder_results[0]
            score = recipe_dict.get("match_score", 0.0)
            if score > best_score:
                best_score = score
                best_recipe = recipe_dict

    # Try SequenceMatcher (always, for comparison)
    sequence_recipe = engine.get_recipe_by_dish(top.label, threshold=0.6)
    if sequence_recipe:
        # SequenceMatcher scores are 0-1, so we can compare directly
        score = sequence_recipe.get("match_score", 0.0)
        if score > best_score:
            best_score = score
            best_recipe = sequence_recipe

    if best_recipe:
        recipes = [best_recipe]

    recipe_dict = recipes[0] if recipes else None
    recipe = Recipe(**recipe_dict) if recipe_dict else None

    context = ContextRetriever.build_context(
        dish=top.label,
        dish_confidence=top.confidence,
        recipes=recipes,
    )

    return DishRecipeResponse(
        predictions=predictions,
        top_label=top.label,
        top_confidence=top.confidence,
        recipe=recipe,
        context=context,
    )
