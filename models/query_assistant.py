"""
Query Assistant (Ollama-backed Grounded QA)
===========================================
Uses a locally-running Ollama model (llama3.2-vision by default) to answer
user questions grounded in system outputs such as detected dishes,
ingredients, recipes, substitutions, and nearby places.

Supports both text-only (Qwen2.5) and multimodal (Llama 3.2-Vision) models.

Prerequisites
-------------
1. Install Ollama: https://ollama.com
2. Pull the model: ollama pull llama3.2-vision (or qwen2.5:3b for text-only)
3. Start Ollama: ollama serve  (or it runs as a background service)

Usage
-----
    from models.query_assistant import QueryAssistant
    from PIL import Image

    assistant = QueryAssistant(model_name="llama3.2-vision")
    assistant.load_model()   # verifies Ollama is reachable

    # Text-only answer
    answer = assistant.answer_with_history(
        question="What's a good recipe for pasta?",
        context={"recipes": [...]},
        history=[],
    )

    # Multimodal answer with image
    image = Image.open("dish.jpg")
    answer = assistant.answer_with_image(
        question="What dish is this and how do I make it?",
        image=image,
        context={"recipes": [...]},
    )
"""

from typing import Dict, Any, List, Optional
from PIL import Image
import base64
from io import BytesIO

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

    DEFAULT_MODEL = "qwen2.5:3b"  # Text-only, lightweight, reliable; llama3.2-vision available but resource-intensive
    DEFAULT_OLLAMA_URL = "http://localhost:11434"

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        ollama_url: str = DEFAULT_OLLAMA_URL,
        max_tokens: int = 1024,
        temperature: float = 0.45,
        top_p: float = 0.9,
        repeat_penalty: float = 1.1,
    ):
        self.model_name = model_name
        self.ollama_url = ollama_url.rstrip("/")
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.repeat_penalty = repeat_penalty
        self._loaded = False

        self.prompt_builder = PromptBuilder()
        self.context_retriever = ContextRetriever()

    # ------------------------------------------------------------------
    # Connection check
    # ------------------------------------------------------------------
    def load_model(self) -> None:
        """Verify that Ollama is running and the model is available.

        Falls back to qwen2.5:3b if llama3.2-vision is not available.
        """
        import requests

        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            resp.raise_for_status()
            available = [m["name"] for m in resp.json().get("models", [])]

            # Check if requested model is available
            model_base = self.model_name.split(":")[0]
            if any(model_base in n for n in available):
                print(f"[OK] Ollama connected. Model: {self.model_name}")
                self._loaded = True
                return

            # Fallback: if llama3.2-vision not available, try qwen2.5:3b
            if "llama3.2-vision" in self.model_name and "qwen2.5" in available:
                print(
                    f"[WARN] Model 'llama3.2-vision' not found. Falling back to qwen2.5:3b"
                )
                self.model_name = "qwen2.5:3b"
                print(f"[OK] Ollama connected. Model: {self.model_name}")
                self._loaded = True
                return

            # Neither available
            print(
                f"[WARN] Model '{self.model_name}' not found in Ollama. "
                f"Available: {available}\n"
                f"[INFO] Run: ollama pull {self.model_name}\n"
                f"[INFO] Or for text-only: ollama pull qwen2.5:3b"
            )
            self._loaded = True  # Still allow fallback template responses

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
            "You are ChefBot, an expert culinary AI assistant powered by SmartKitchen. "
            "Respond with practical, detailed answers grounded in the context below.\n\n"
            "Response format:\n"
            "• Use numbered steps for recipes or techniques\n"
            "• Use bullet points for ingredient lists\n"
            "• Include prep time and difficulty when available\n"
            "• Provide both metric and imperial measurements\n"
            "• Keep responses under 300 words unless a full recipe is requested\n"
            "• Say 'I don't have that information' if the context doesn't contain the answer\n\n"
            f"Context:\n{context_block}"
        )

        messages = [{"role": "system", "content": system_content}]
        # Include last 5 turns of conversation history (was 3)
        for turn in (history or [])[-5:]:
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

    def answer_with_image(
        self,
        question: str,
        image: Image.Image,
        context: Dict[str, Any] = None,
        history: List[Dict] = None,
    ) -> str:
        """Generate a grounded answer using Ollama with multimodal image support.

        Requires a vision-capable model like llama3.2-vision.
        Falls back to text-only answer if model doesn't support images.

        Parameters
        ----------
        question : str
            User's question about the image
        image : PIL.Image
            Image to analyze
        context : dict, optional
            Context dict with recipes, ingredients, etc.
        history : list, optional
            Conversation history

        Returns
        -------
        str
            Model's response
        """
        if not self._loaded:
            return self._fallback_answer(question, context or {})

        # Encode image to base64
        image_b64 = self._encode_image(image)

        # Build context block if provided
        context_block = ""
        if context:
            filtered = self.context_retriever.retrieve_for_question(question, context)
            context_block = self.prompt_builder._format_context(filtered)

        system_content = (
            "You are ChefBot, an expert culinary AI assistant powered by SmartKitchen. "
            "You have the ability to see images. Analyze the image and provide practical, detailed answers.\n\n"
            "Response format:\n"
            "• Use numbered steps for recipes or techniques\n"
            "• Use bullet points for ingredient lists\n"
            "• Include prep time and difficulty when available\n"
            "• Provide both metric and imperial measurements\n"
            "• Describe what you see in the image\n"
            "• Say 'I don't have that information' if the context doesn't contain the answer\n\n"
        )

        if context_block:
            system_content += f"Context:\n{context_block}\n\n"

        messages = [{"role": "system", "content": system_content}]

        # Add conversation history
        for turn in (history or [])[-5:]:
            messages.append({"role": "user", "content": turn["question"]})
            messages.append({"role": "assistant", "content": turn["answer"]})

        # Add current question with image
        messages.append({
            "role": "user",
            "content": question,
            "images": [image_b64]
        })

        return self._call_ollama(messages)

    # ------------------------------------------------------------------
    # Helper: Image encoding
    # ------------------------------------------------------------------
    @staticmethod
    def _encode_image(image: Image.Image) -> str:
        """Convert PIL Image to base64 string for Ollama."""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_b64 = base64.b64encode(buffered.getvalue()).decode()
        return img_b64

    # ------------------------------------------------------------------
    # Ollama HTTP call
    # ------------------------------------------------------------------
    def _call_ollama(self, messages: List[Dict]) -> str:
        import requests
        import time

        try:
            # Determine timeout based on model type (vision models are slower on first inference)
            timeout = 600 if "vision" in self.model_name.lower() else 300

            print(f"[QueryAssistant] Calling {self.model_name} with {timeout}s timeout...")
            start_time = time.time()

            resp = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "num_predict": self.max_tokens,
                        "temperature": self.temperature,
                        "top_p": self.top_p,
                        "repeat_penalty": self.repeat_penalty,
                    },
                },
                timeout=timeout,
            )
            elapsed = time.time() - start_time
            print(f"[QueryAssistant] Response received in {elapsed:.1f}s")

            resp.raise_for_status()
            return resp.json()["message"]["content"].strip()
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            return (
                f"Request timed out after {elapsed:.0f}s. Vision models can be slow on first inference. "
                f"Try again—the model may already be in memory. If issues persist, check Ollama resources via `ollama ps`."
            )
        except requests.exceptions.ConnectionError:
            return f"Cannot connect to Ollama at {self.ollama_url}. Is Ollama running? Try: ollama serve"
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
