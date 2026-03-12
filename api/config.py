from pathlib import Path

# Project root (one level up from api/)
PROJECT_ROOT = Path(__file__).parent.parent

# Data paths
RECIPES_PATH = str(PROJECT_ROOT / "data" / "recipes.json")
SUBSTITUTIONS_PATH = str(PROJECT_ROOT / "data" / "substitutions.json")

# Model checkpoint paths
DISH_CHECKPOINT = str(PROJECT_ROOT / "outputs" / "saved_models" / "dish_classifier_best.pth")
INGREDIENT_CHECKPOINT = str(PROJECT_ROOT / "outputs" / "saved_models" / "ingredient_classifier_best.pth")

# CORS
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
