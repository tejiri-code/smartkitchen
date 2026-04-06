"""
Singleton model loaders.
Call startup_models() once at app lifespan start.
Each get_*() function returns the cached instance.
"""
from pathlib import Path
from typing import Optional

from api.config import (
    RECIPES_PATH,
    SUBSTITUTIONS_PATH,
    DISH_CHECKPOINT,
    INGREDIENT_CHECKPOINT,
)

from utils.recipe_engine import RecipeEngine
from utils.location_service import LocationService

# ML model imports are lazy-loaded to speed up server startup
# They will be imported on first use or in background during startup

_dish_model: Optional[DishClassifier] = None
_ingredient_model: Optional[IngredientClassifier] = None
_query_assistant: Optional[QueryAssistant] = None
_recipe_engine: Optional[RecipeEngine] = None
_location_service: Optional[LocationService] = None
_joint_embedder: Optional[JointEmbedder] = None
_hf_model_loaded: bool = False


def startup_models() -> None:
    global _dish_model, _ingredient_model, _query_assistant
    global _recipe_engine, _location_service, _joint_embedder

    # Lazy imports inside function to speed up server startup
    from models.dish_classifier import DishClassifier, DEFAULT_CLASSES
    from models.ingredient_classifier import IngredientClassifier, INGREDIENT_CLASSES
    from models.query_assistant import QueryAssistant
    from models.joint_embedder import JointEmbedder

    # Recipe engine + location service (no GPU needed)
    _recipe_engine = RecipeEngine(
        recipes_path=RECIPES_PATH,
        substitutions_path=SUBSTITUTIONS_PATH,
    )
    _location_service = LocationService(use_sample_fallback=True)

    # Joint embedder for recipe retrieval
    _joint_embedder = JointEmbedder(embedding_dim=128)
    _joint_embedder.build_recipe_index(_recipe_engine.recipes)
    print("[OK] Joint embedder built with TF-IDF + SVD recipe index.")

    # Dish classifier (CLIP-based zero-shot, no training needed)
    _dish_model = DishClassifier(num_classes=len(DEFAULT_CLASSES))
    _dish_model.load_model()  # Load pretrained CLIP
    print(f"[OK] Dish classifier initialized (CLIP zero-shot)")

    # Ingredient classifier (CLIP-based zero-shot, no training needed)
    _ingredient_model = IngredientClassifier(
        num_classes=len(INGREDIENT_CLASSES),
        model_name="ViT-L/14",
    )
    print(f"[OK] Ingredient classifier initialized (CLIP ViT-L/14 zero-shot)")

    # Query assistant (template fallback by default; HF model loaded lazily)
    _query_assistant = QueryAssistant()


def ensure_ollama_available() -> None:
    """Connect to Ollama on first request if not already done."""
    global _hf_model_loaded
    if not _hf_model_loaded and _query_assistant is not None:
        _query_assistant.load_model()
        _hf_model_loaded = True


def get_dish_model() -> DishClassifier:
    return _dish_model


def get_ingredient_model() -> IngredientClassifier:
    return _ingredient_model


def get_query_assistant() -> QueryAssistant:
    return _query_assistant


def get_recipe_engine() -> RecipeEngine:
    return _recipe_engine


def get_location_service() -> LocationService:
    return _location_service


def get_joint_embedder() -> JointEmbedder:
    return _joint_embedder
