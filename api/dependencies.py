"""
Singleton model loaders with lazy initialization.
- startup_models() loads only lightweight components (RecipeEngine, LocationService, JointEmbedder)
- Heavy models (DishClassifier, IngredientClassifier, QueryAssistant) load on first access
- This keeps startup memory <100MB and allows Render health checks to pass quickly
"""
from pathlib import Path
from typing import Optional, Any

from api.config import (
    RECIPES_PATH,
    SUBSTITUTIONS_PATH,
    DISH_CHECKPOINT,
    INGREDIENT_CHECKPOINT,
)

from utils.recipe_engine import RecipeEngine
from utils.location_service import LocationService

# Cache for lazy-loaded models
_models_cache: dict[str, Any] = {}
_recipe_engine: Optional[RecipeEngine] = None
_location_service: Optional[LocationService] = None
_joint_embedder: Optional[Any] = None


def startup_models() -> None:
    """Load only lightweight, non-GPU components. Heavy models load on-demand."""
    global _recipe_engine, _location_service, _joint_embedder

    # Recipe engine + location service (no GPU, fast)
    _recipe_engine = RecipeEngine(
        recipes_path=RECIPES_PATH,
        substitutions_path=SUBSTITUTIONS_PATH,
    )
    _location_service = LocationService(use_sample_fallback=True)
    print("[OK] RecipeEngine + LocationService loaded")

    # Joint embedder for recipe retrieval (CPU only, but needs recipe index)
    from models.joint_embedder import JointEmbedder
    _joint_embedder = JointEmbedder(embedding_dim=128)
    _joint_embedder.build_recipe_index(_recipe_engine.recipes)
    print("[OK] Joint embedder built with TF-IDF + SVD recipe index")


def _load_dish_model() -> Any:
    """Lazy load dish classifier on first use."""
    if "dish_model" not in _models_cache:
        from models.dish_classifier import DishClassifier, DEFAULT_CLASSES
        model = DishClassifier(num_classes=len(DEFAULT_CLASSES))
        model.load_model()
        _models_cache["dish_model"] = model
        print("[OK] Dish classifier loaded (CLIP ViT-L/14)")
    return _models_cache["dish_model"]


def _load_ingredient_model() -> Any:
    """Lazy load ingredient classifier on first use."""
    if "ingredient_model" not in _models_cache:
        from models.ingredient_classifier import IngredientClassifier, INGREDIENT_CLASSES
        model = IngredientClassifier(
            num_classes=len(INGREDIENT_CLASSES),
            model_name="ViT-L/14",
        )
        _models_cache["ingredient_model"] = model
        print("[OK] Ingredient classifier loaded (CLIP ViT-L/14)")
    return _models_cache["ingredient_model"]


def _load_query_assistant() -> Any:
    """Lazy load query assistant on first use."""
    if "query_assistant" not in _models_cache:
        from models.query_assistant import QueryAssistant
        model = QueryAssistant()
        _models_cache["query_assistant"] = model
        print("[OK] Query assistant loaded")
    return _models_cache["query_assistant"]


def get_dish_model() -> Any:
    """Get dish classifier, loading it on first call."""
    return _load_dish_model()


def get_ingredient_model() -> Any:
    """Get ingredient classifier, loading it on first call."""
    return _load_ingredient_model()


def get_query_assistant() -> Any:
    """Get query assistant, loading it on first call."""
    return _load_query_assistant()


def ensure_ollama_available() -> None:
    """Connect to Ollama on first request if not already done."""
    assistant = get_query_assistant()
    if hasattr(assistant, '_ollama_loaded') and not assistant._ollama_loaded:
        assistant.load_model()
        assistant._ollama_loaded = True


def get_recipe_engine() -> RecipeEngine:
    """Get recipe engine (always loaded at startup)."""
    return _recipe_engine


def get_location_service() -> LocationService:
    """Get location service (always loaded at startup)."""
    return _location_service


def get_joint_embedder() -> Any:
    """Get joint embedder (always loaded at startup)."""
    return _joint_embedder
