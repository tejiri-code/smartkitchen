"""
Query Assistant (Ollama-backed Grounded QA)
===========================================
Uses a locally-running Ollama model (qwen2.5:3b by default) to answer
user questions grounded in system outputs such as detected dishes,
ingredients, recipes, substitutions, and nearby places.

Prerequisites
-------------
1. Install Ollama: https://ollama.com
2. Pull the model: ollama pull qwen2.5:3b
3. Start Ollama: ollama serve  (or it runs as a background service)

Usage
-----
    from models.query_assistant import QueryAssistant

    assistant = QueryAssistant()
    assistant.load_model()   # verifies Ollama is reachable

    answer = assistant.answer_with_history(
        question="Give me a recipe for Baby Back Ribs",
        context={"detected_dish": "Baby Back Ribs", "recipes": [...]},
        history=[],
    )
"""

from typing import Dict, Any, List

from utils.prompt_builder import PromptBuilder
from utils.retrieval import ContextRetriever


class QueryAssistant:
    """Grounded query assistant powered by a locally-running Ollama model.

    Parameters
    ----------
    model_name : str
        Ollama model identifier (e.g. 'qwen2.5:3b', 'llama3.2:3b').
    ollama_url : str
        Base URL of the Ollama server.
    max_tokens : int
        Maximum tokens in the generated response.
    temperature : float
        Sampling temperature.
    """

    DEFAULT_MODEL = "qwen2.5:3b"
    DEFAULT_OLLAMA_URL = "http://localhost:11434"

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        ollama_url: str = DEFAULT_OLLAMA_URL,
        max_tokens: int = 512,
        temperature: float = 0.4,
    ):
        self.model_name = model_name
        self.ollama_url = ollama_url.rstrip("/")
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._loaded = False

        self.prompt_builder = PromptBuilder()
        self.context_retriever = ContextRetriever()

    # ------------------------------------------------------------------
    # Connection check
    # ------------------------------------------------------------------
    def load_model(self) -> None:
        """Verify that Ollama is running and the model is available."""
        import requests

        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            resp.raise_for_status()
            available = [m["name"] for m in resp.json().get("models", [])]
            if not any(self.model_name.split(":")[0] in n for n in available):
                print(
                    f"[WARN] Model '{self.model_name}' not found in Ollama. "
                    f"Available: {available}\n"
                    f"[INFO] Run: ollama pull {self.model_name}"
                )
            else:
                print(f"[OK] Ollama connected. Model: {self.model_name}")
            self._loaded = True
        except Exception as e:
            print(f"[WARN] Could not connect to Ollama at {self.ollama_url}: {e}")
            self._loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    # ------------------------------------------------------------------
    # Answer generation
    # ------------------------------------------------------------------
    def answer(
        self,
        question: str,
        context: Dict[str, Any],
        history: List[Dict] = None,
    ) -> str:
        """Generate a grounded answer using Ollama, falling back to
        template responses if Ollama is unavailable."""
        if not self._loaded:
            return self._fallback_answer(question, context)

        filtered = self.context_retriever.retrieve_for_question(question, context)
        context_block = self.prompt_builder._format_context(filtered)

        system_content = (
            "You are a helpful cooking assistant. "
            "Use the context below to give accurate, specific answers about "
            "recipes, cooking techniques, ingredients, and substitutions. "
            "If asked for a recipe, provide the full ingredients list and steps. "
            "Be concise and practical.\n\n"
            f"Context:\n{context_block}"
        )

        messages = [{"role": "system", "content": system_content}]
        for turn in (history or [])[-3:]:
            messages.append({"role": "user", "content": turn["question"]})
            messages.append({"role": "assistant", "content": turn["answer"]})
        messages.append({"role": "user", "content": question})

        return self._call_ollama(messages)

    def answer_with_history(
        self,
        question: str,
        context: Dict[str, Any],
        history: List[Dict],
    ) -> str:
        return self.answer(question, context, history=history)

    # ------------------------------------------------------------------
    # Ollama HTTP call
    # ------------------------------------------------------------------
    def _call_ollama(self, messages: List[Dict]) -> str:
        import requests

        try:
            resp = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "num_predict": self.max_tokens,
                        "temperature": self.temperature,
                    },
                },
                timeout=60,
            )
            resp.raise_for_status()
            return resp.json()["message"]["content"].strip()
        except Exception as e:
            return f"Error reaching Ollama: {e}. Is Ollama running? Try: ollama serve"

    # ------------------------------------------------------------------
    # Fallback (Ollama not available)
    # ------------------------------------------------------------------
    def _fallback_answer(self, question: str, context: Dict[str, Any]) -> str:
        """Template-based responses when Ollama is not running."""
        q_lower = question.lower()

        # Recipe questions
        if any(kw in q_lower for kw in ["recipe", "how to make", "how do i make", "instructions", "steps"]):
            if "recipes" in context and context["recipes"]:
                recipe = context["recipes"][0]
                name = recipe.get("name", "this dish")
                ings = ", ".join(recipe.get("ingredients", []))
                steps = recipe.get("steps", [])
                resp = f"Recipe for {name}:\n\nIngredients: {ings}."
                if steps:
                    resp += "\n\nSteps:\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))
                return resp
            if "detected_dish" in context:
                return (
                    f"I don't have a recipe for {context['detected_dish']} in the database. "
                    "Enable Qwen (Ollama) in Settings for AI-generated recipes."
                )

        # Ingredient questions
        if any(kw in q_lower for kw in ["ingredient", "what do i need", "what am i missing"]):
            if "recipes" in context and context["recipes"]:
                recipe = context["recipes"][0]
                ings = ", ".join(recipe.get("ingredients", []))
                missing = recipe.get("missing_ingredients", [])
                resp = f"For {recipe['name']}, you need: {ings}."
                if missing:
                    resp += f" You're missing: {', '.join(missing)}."
                return resp

        # Time questions
        if any(kw in q_lower for kw in ["how long", "time", "minutes", "quick"]):
            if "recipes" in context and context["recipes"]:
                recipe = context["recipes"][0]
                return f"{recipe['name']} takes approximately {recipe.get('prep_time', 'unknown time')}."

        # Substitution questions
        if any(kw in q_lower for kw in ["instead", "substitute", "replace", "swap"]):
            if "substitutions" in context:
                lines = []
                for sub in context["substitutions"]:
                    alts = ", ".join(sub.get("alternatives", [])[:3])
                    lines.append(f"Instead of {sub['ingredient']}, you can use: {alts}.")
                return " ".join(lines) if lines else "No substitution information available."

        # Location questions
        if any(kw in q_lower for kw in ["where", "nearby", "buy", "order", "restaurant", "grocery"]):
            if "nearby_places" in context:
                places = context["nearby_places"][:3]
                lines = [
                    f"{p['name']} ({p.get('distance_km', '?')} km away)"
                    for p in places
                ]
                return "Here are some nearby options: " + "; ".join(lines) + "."

        # Vegetarian / dietary
        if any(kw in q_lower for kw in ["vegetarian", "vegan", "dairy-free", "gluten-free"]):
            if "substitutions" in context:
                return (
                    "You can make dietary substitutions using the alternatives listed. "
                    "Check the substitution suggestions for plant-based or allergen-free options."
                )

        if "detected_dish" in context:
            return (
                f"I can see you're asking about {context['detected_dish']}. "
                "Enable Qwen (Ollama) in Settings for detailed AI answers, "
                "or try asking about ingredients, recipe steps, or substitutions."
            )

        return "Enable Qwen (Ollama) in Settings for AI-powered answers to any cooking question."
