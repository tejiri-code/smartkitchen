"""
Context Retrieval Module
========================
Aggregates structured context from system outputs (dish predictions,
detected ingredients, recipes, substitutions, nearby places) and
selects the relevant subset for each user question so the Query
Assistant can generate grounded answers.
"""

from typing import Dict, List, Optional, Any


class ContextRetriever:
    """Builds and filters context dictionaries for RAG-style prompting."""

    # Keywords used to decide which context sections are relevant
    _LOCATION_KEYWORDS = {
        "where", "nearby", "close", "closest", "near me", "buy",
        "order", "restaurant", "grocery", "store", "shop", "deliver",
    }
    _SUBSTITUTION_KEYWORDS = {
        "substitute", "substitution", "replace", "instead", "swap",
        "alternative", "allergy", "intolerant", "vegan", "vegetarian",
        "dairy-free", "gluten-free",
    }
    _RECIPE_KEYWORDS = {
        "recipe", "cook", "make", "prepare", "ingredient", "step",
        "how to", "instructions", "method", "time", "long",
        "minutes", "quick", "easy",
    }
    _MISSING_KEYWORDS = {
        "missing", "need", "don't have", "haven't got", "lack",
        "short of", "what am i missing", "what do i need",
    }

    # ------------------------------------------------------------------
    # Context building
    # ------------------------------------------------------------------
    @staticmethod
    def build_context(
        dish: Optional[str] = None,
        dish_confidence: Optional[float] = None,
        ingredients: Optional[List[str]] = None,
        recipes: Optional[List[Dict]] = None,
        missing_ingredients: Optional[List[str]] = None,
        substitutions: Optional[List[Dict]] = None,
        nearby_places: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """Assemble a full context dictionary from available system outputs."""
        ctx: Dict[str, Any] = {}

        if dish:
            ctx["detected_dish"] = dish
        if dish_confidence is not None:
            ctx["dish_confidence"] = dish_confidence
        if ingredients:
            ctx["detected_ingredients"] = ingredients
        if recipes:
            ctx["recipes"] = recipes
        if missing_ingredients:
            ctx["missing_ingredients"] = missing_ingredients
        if substitutions:
            ctx["substitutions"] = substitutions
        if nearby_places:
            ctx["nearby_places"] = nearby_places

        return ctx

    # ------------------------------------------------------------------
    # Relevance filtering
    # ------------------------------------------------------------------
    def retrieve_for_question(
        self, question: str, full_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Select the context sections most relevant to the user's
        question to keep prompts focused and concise."""
        q_lower = question.lower()
        relevant: Dict[str, Any] = {}

        # Always include dish / ingredient context (lightweight)
        if "detected_dish" in full_context:
            relevant["detected_dish"] = full_context["detected_dish"]
        if "dish_confidence" in full_context:
            relevant["dish_confidence"] = full_context["dish_confidence"]
        if "detected_ingredients" in full_context:
            relevant["detected_ingredients"] = full_context["detected_ingredients"]

        # Conditionally include heavier sections
        if self._matches_any(q_lower, self._RECIPE_KEYWORDS):
            if "recipes" in full_context:
                relevant["recipes"] = full_context["recipes"]

        if self._matches_any(q_lower, self._MISSING_KEYWORDS):
            if "missing_ingredients" in full_context:
                relevant["missing_ingredients"] = full_context["missing_ingredients"]
            # Also pull substitutions for missing items
            if "substitutions" in full_context:
                relevant["substitutions"] = full_context["substitutions"]

        if self._matches_any(q_lower, self._SUBSTITUTION_KEYWORDS):
            if "substitutions" in full_context:
                relevant["substitutions"] = full_context["substitutions"]

        if self._matches_any(q_lower, self._LOCATION_KEYWORDS):
            if "nearby_places" in full_context:
                relevant["nearby_places"] = full_context["nearby_places"]

        # Fallback: if nothing specific matched, include recipes + substitutions
        extra_keys = set(relevant.keys()) - {
            "detected_dish", "dish_confidence", "detected_ingredients"
        }
        if not extra_keys:
            for key in ("recipes", "substitutions", "missing_ingredients"):
                if key in full_context:
                    relevant[key] = full_context[key]

        return relevant

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _matches_any(text: str, keywords: set) -> bool:
        return any(kw in text for kw in keywords)


# ======================================================================
# Quick self-test
# ======================================================================
if __name__ == "__main__":
    cr = ContextRetriever()

    full_ctx = ContextRetriever.build_context(
        dish="spaghetti bolognese",
        dish_confidence=0.91,
        ingredients=["pasta", "tomato", "onion", "garlic"],
        recipes=[{"name": "Spaghetti Bolognese", "prep_time": "35 minutes"}],
        missing_ingredients=["minced beef"],
        substitutions=[{"ingredient": "minced beef", "alternatives": ["lentils"]}],
        nearby_places=[{"name": "Bella Pasta", "distance": "0.8 km"}],
    )

    q1 = "Where can I order this nearby?"
    print(f"Q: {q1}")
    print(f"Relevant context keys: {list(cr.retrieve_for_question(q1, full_ctx).keys())}")

    q2 = "What can I use instead of minced beef?"
    print(f"\nQ: {q2}")
    print(f"Relevant context keys: {list(cr.retrieve_for_question(q2, full_ctx).keys())}")
