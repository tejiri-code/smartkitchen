"""
Prompt Builder
==============
Constructs context-aware prompts for the Query Assistant (FLAN-T5).
Formats structured system outputs into a text prompt that instructs
the model to answer only from retrieved context.
"""

from typing import Dict, Any, List, Optional


# ------------------------------------------------------------------
# System preamble (instruction prefix for the generative model)
# ------------------------------------------------------------------
_SYSTEM_PREAMBLE = (
    "You are ChefBot, a helpful cooking expert. "
    "Answer using ONLY the provided context. "
    "Format your response with clear structure:\n"
    "- Use ### for recipe titles\n"
    "- Use **Bold** for section headers like **Ingredients:** and **Cooking Steps:**\n"
    "- Use - for ingredient lists\n"
    "- Use numbered lists for steps\n"
    "- Keep explanations concise and practical\n"
    "Do not invent ingredients or steps not in the context. "
    "If information is unavailable, say so clearly.\n\n"
)

# Maximum character budget for context block (to fit within model limits)
_MAX_CONTEXT_CHARS = 2500


class PromptBuilder:
    """Builds FLAN-T5-ready prompt strings from structured context."""

    def __init__(self, max_context_chars: int = _MAX_CONTEXT_CHARS):
        self.max_context_chars = max_context_chars

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------
    def build_prompt(self, question: str, context: Dict[str, Any]) -> str:
        """Build a full prompt string from the user question and a
        context dict (as produced by ``ContextRetriever``)."""
        context_block = self._format_context(context)

        # Truncate context if it exceeds the budget
        if len(context_block) > self.max_context_chars:
            context_block = context_block[: self.max_context_chars] + "\n[context truncated]"

        prompt = (
            f"{_SYSTEM_PREAMBLE}"
            f"Context:\n{context_block}\n\n"
            f"User question: {question}\n\n"
            f"Answer:"
        )
        return prompt

    # ------------------------------------------------------------------
    # Context formatting
    # ------------------------------------------------------------------
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Convert the context dict into a readable text block."""
        sections: List[str] = []

        # Detected dish
        if "detected_dish" in context:
            conf = context.get("dish_confidence")
            conf_str = f" (confidence: {conf:.0%})" if conf is not None else ""
            sections.append(f"Detected dish: {context['detected_dish']}{conf_str}")

        # Detected ingredients
        if "detected_ingredients" in context:
            ings = ", ".join(context["detected_ingredients"])
            sections.append(f"Detected ingredients: {ings}")

        # Recipes
        if "recipes" in context:
            sections.append(self._format_recipes(context["recipes"]))

        # Missing ingredients
        if "missing_ingredients" in context:
            missing = ", ".join(context["missing_ingredients"])
            sections.append(f"Missing ingredients: {missing}")

        # Substitutions
        if "substitutions" in context:
            sections.append(self._format_substitutions(context["substitutions"]))

        # Nearby places
        if "nearby_places" in context:
            sections.append(self._format_places(context["nearby_places"]))

        return "\n".join(sections)

    # ------------------------------------------------------------------
    # Section formatters
    # ------------------------------------------------------------------
    @staticmethod
    def _format_recipes(recipes: List[Dict]) -> str:
        lines = []
        for i, r in enumerate(recipes[:5], 1):
            name = r.get("name", "Unknown")
            prep = r.get("prep_time", "N/A")
            cuisine = r.get("cuisine", "")
            ings = r.get("ingredients", [])
            steps = r.get("steps", [])
            score = r.get("score")

            # Recipe header with markdown
            cuisine_str = f" [{cuisine}]" if cuisine else ""
            score_str = f" — {int(score*100)}% match" if score is not None else ""
            lines.append(f"### Recipe {i}: {name}{cuisine_str}")
            lines.append(f"**Time:** {prep}{score_str}")
            lines.append("")

            # Ingredients as bullet list
            if ings:
                lines.append("**Ingredients:**")
                for ing in ings:
                    lines.append(f"- {ing}")
                lines.append("")

            # Steps as numbered list
            if steps:
                lines.append("**Cooking Steps:**")
                for j, step in enumerate(steps[:6], 1):  # Limit to 6 steps
                    lines.append(f"{j}. {step}")
                if len(steps) > 6:
                    lines.append(f"+ {len(steps) - 6} more step{'s' if len(steps) - 6 != 1 else ''}")
                lines.append("")

        return "\n".join(lines) if lines else "No recipes found."

    @staticmethod
    def _format_substitutions(substitutions: List[Dict]) -> str:
        lines = ["=== SUBSTITUTIONS ==="]
        for sub in substitutions:
            ing = sub.get("ingredient", "?")
            alts = ", ".join(sub.get("alternatives", []))
            notes = sub.get("notes", "")
            lines.append(f"  • {ing} → {alts}")
            if notes:
                lines.append(f"    (Note: {notes})")
        return "\n".join(lines)

    @staticmethod
    def _format_places(places: List[Dict]) -> str:
        lines = ["=== NEARBY PLACES ==="]
        for p in places:
            name = p.get("name", "Unknown")
            dist = p.get("distance_km", "?")
            addr = p.get("address", "")
            cat = p.get("category", "")
            rating = p.get("rating")
            rating_str = f" — Rating: {rating}/5" if rating else ""
            lines.append(f"  • {name} ({cat})")
            lines.append(f"    {dist} km away | {addr}{rating_str}")
        return "\n".join(lines)


# ======================================================================
# Quick self-test
# ======================================================================
if __name__ == "__main__":
    pb = PromptBuilder()

    ctx = {
        "detected_dish": "spaghetti bolognese",
        "dish_confidence": 0.91,
        "recipes": [
            {
                "name": "Spaghetti Bolognese",
                "ingredients": ["pasta", "tomato", "onion", "garlic"],
                "steps": ["Cook pasta", "Make sauce", "Combine"],
                "prep_time": "35 minutes",
            }
        ],
        "nearby_places": [
            {"name": "Bella Pasta", "distance_km": 0.8, "address": "12 High St", "category": "restaurant", "rating": 4.3},
        ],
    }

    prompt = pb.build_prompt("Where can I order this nearby?", ctx)
    print(prompt)
