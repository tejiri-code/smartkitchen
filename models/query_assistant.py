"""
Query Assistant (RAG-style Grounded QA)
=======================================
Uses a Hugging Face generative model (FLAN-T5-small by default) to
answer user questions grounded in system outputs such as detected
dishes, ingredients, recipes, substitutions, and nearby places.

Usage
-----
    from models.query_assistant import QueryAssistant

    assistant = QueryAssistant()
    assistant.load_model()

    answer = assistant.answer(
        question="What can I use instead of milk?",
        context={"detected_ingredients": [...], "substitutions": [...]}
    )
"""

from typing import Dict, Any, Optional

from utils.prompt_builder import PromptBuilder
from utils.retrieval import ContextRetriever


class QueryAssistant:
    """Grounded query assistant powered by a Hugging Face seq2seq model.

    Parameters
    ----------
    model_name : str
        Hugging Face model identifier.
    max_new_tokens : int
        Maximum tokens in the generated answer.
    temperature : float
        Sampling temperature (higher = more creative, lower = more focused).
    device : str
        Device to run the model on ('cpu' or 'cuda').
    """

    DEFAULT_MODEL = "google/flan-t5-small"

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        max_new_tokens: int = 200,
        temperature: float = 0.3,
        device: str = "cpu",
    ):
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        
        # Auto-detect best device if default (cpu) or cuda (on mac) is requested
        import torch
        if device == "cuda" and not torch.cuda.is_available():
            if torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        elif device == "cpu":
            if torch.backends.mps.is_available():
                self.device = "mps"
            elif torch.cuda.is_available():
                self.device = "cuda"
            else:
                self.device = "cpu"
        else:
            self.device = device

        self.model = None
        self.tokenizer = None
        self._loaded = False

        self.prompt_builder = PromptBuilder()
        self.context_retriever = ContextRetriever()

    # ------------------------------------------------------------------
    # Model loading
    # ------------------------------------------------------------------
    def load_model(self):
        """Load the tokenizer and model from Hugging Face."""
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        import torch

        print(f"Loading model: {self.model_name} on {self.device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # Use device_map if CUDA is available, otherwise use to(device)
        if self.device == "cuda":
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_name, device_map="auto"
            )
        elif self.device == "mps":
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self.model.to(torch.device("mps"))
        else:
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self.model.to(self.device)
            
        self.model.eval()
        self._loaded = True
        print("Model loaded successfully.")

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
        use_retrieval_filter: bool = True,
    ) -> str:
        """Generate a grounded answer to the user's question.

        Parameters
        ----------
        question : str
            Natural-language question from the user.
        context : dict
            Full context dict (from ContextRetriever.build_context).
        use_retrieval_filter : bool
            If True, filter context to the most relevant sections first.

        Returns
        -------
        str
            Generated answer text.
        """
        if not self._loaded:
            return self._fallback_answer(question, context)

        # Optionally filter context
        if use_retrieval_filter:
            context = self.context_retriever.retrieve_for_question(
                question, context
            )

        # Build prompt
        prompt = self.prompt_builder.build_prompt(question, context)

        # Tokenize
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=512,
            truncation=True,
        ).to(self.device)

        # Generate
        import torch

        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                temperature=self.temperature,
                do_sample=self.temperature > 0,
                top_p=0.9,
                repetition_penalty=1.2,
            )

        answer = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)

        # Post-process
        answer = answer.strip()
        if not answer:
            answer = "I don't have enough information to answer that question based on the available context."

        return answer

    # ------------------------------------------------------------------
    # Fallback (no model loaded — uses template-based responses)
    # ------------------------------------------------------------------
    def _fallback_answer(
        self, question: str, context: Dict[str, Any]
    ) -> str:
        """Provide a reasonable template-based answer when the model
        is not loaded (e.g. during demo without GPU)."""
        q_lower = question.lower()

        # Ingredient questions
        if any(kw in q_lower for kw in ["ingredient", "what do i need", "what am i missing"]):
            if "recipes" in context and context["recipes"]:
                recipe = context["recipes"][0]
                ings = ", ".join(recipe.get("ingredients", []))
                missing = recipe.get("missing_ingredients", [])
                response = f"For {recipe['name']}, you need: {ings}."
                if missing:
                    response += f" You're missing: {', '.join(missing)}."
                return response

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
                    f"{p['name']} ({p.get('distance_km', '?')} km away, {p.get('address', '')})"
                    for p in places
                ]
                return "Here are some nearby options: " + "; ".join(lines) + "."

        # Vegetarian / dietary
        if any(kw in q_lower for kw in ["vegetarian", "vegan", "dairy-free", "gluten-free"]):
            if "substitutions" in context:
                return ("You can make dietary substitutions using the alternatives listed. "
                        "Check the substitution suggestions for plant-based or allergen-free options.")

        # Generic fallback
        if "detected_dish" in context:
            return f"Based on the detected dish ({context['detected_dish']}), I'd recommend checking the recipe details and ingredient list for more information."

        return "I'm here to help with cooking questions. Could you be more specific about what you'd like to know?"

    # ------------------------------------------------------------------
    # Conversation support
    # ------------------------------------------------------------------
    def answer_with_history(
        self,
        question: str,
        context: Dict[str, Any],
        history: list,
    ) -> str:
        """Answer with awareness of prior conversation turns.

        Appends a brief history summary to the context before generating.
        """
        if history:
            history_text = "\n".join(
                [f"Q: {h['question']}\nA: {h['answer']}" for h in history[-3:]]
            )
            context = {**context, "conversation_history": history_text}

        return self.answer(question, context)


# ======================================================================
# Quick self-test
# ======================================================================
if __name__ == "__main__":
    assistant = QueryAssistant()
    # Test fallback mode (no model loaded)
    ctx = {
        "detected_dish": "spaghetti bolognese",
        "recipes": [
            {
                "name": "Spaghetti Bolognese",
                "ingredients": ["pasta", "tomato", "onion", "garlic"],
                "prep_time": "35 minutes",
            }
        ],
        "substitutions": [
            {"ingredient": "pasta", "alternatives": ["rice noodles", "zucchini noodles"]},
        ],
        "nearby_places": [
            {"name": "Bella Pasta", "distance_km": 0.8, "address": "12 High St"},
        ],
    }

    questions = [
        "What ingredients do I need?",
        "How long does this take?",
        "What can I use instead of pasta?",
        "Where can I order this nearby?",
        "Can I make this vegetarian?",
    ]

    print("=== Fallback mode (no model loaded) ===")
    for q in questions:
        print(f"\nQ: {q}")
        print(f"A: {assistant.answer(q, ctx)}")
