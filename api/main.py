import sys
import threading
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is on sys.path so models/ and utils/ are importable
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.config import ALLOWED_ORIGINS
from api.dependencies import startup_models
from api.routers import dish, ingredients, recipes, assistant, places, feedback


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load models in background thread to avoid blocking Render health checks
    def load_models():
        try:
            startup_models()
            print("[OK] All models loaded successfully in background")
        except Exception as e:
            print(f"[ERROR] Failed to load models: {e}")

    thread = threading.Thread(target=load_models, daemon=True)
    thread.start()
    yield


app = FastAPI(title="SmartKitchen API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dish.router,        prefix="/classify",  tags=["Classification"])
app.include_router(ingredients.router, prefix="/classify",  tags=["Classification"])
app.include_router(recipes.router,     prefix="/recipes",   tags=["Recipes"])
app.include_router(assistant.router,   prefix="/assistant", tags=["Assistant"])
app.include_router(places.router,      prefix="/places",    tags=["Places"])
app.include_router(feedback.router,    prefix="/feedback",  tags=["Feedback"])


@app.get("/health")
def health():
    return {"status": "ok"}
