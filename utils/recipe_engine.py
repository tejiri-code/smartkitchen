"""
Recipe Recommendation Engine
=============================
Retrieval-based recipe engine that matches predicted dishes or detected
ingredients to stored recipes, ranks them by overlap, and identifies
missing ingredients with possible substitutions.
"""

import json
from pathlib import Path
from difflib import SequenceMatcher
from typing import List, Dict, Optional, Tuple


class RecipeEngine:
    """Loads recipes and substitutions, provides dish lookup and
    ingredient-based recommendation with scoring."""

    def __init__(
        self,
        recipes_path: str = "data/recipes.json",
        substitutions_path: str = "data/substitutions.json",
    ):
        self.recipes = self._load_json(recipes_path)
        self.substitutions = self._load_json(substitutions_path)

    # ------------------------------------------------------------------
    # I/O helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _load_json(path: str) -> dict | list:
        with open(Path(path), "r", encoding="utf-8") as f:
            return json.load(f)

    # ------------------------------------------------------------------
    # Dish-based lookup
    # ------------------------------------------------------------------
    def get_recipe_by_dish(
        self, dish_name: str, threshold: float = 0.4
    ) -> Optional[Dict]:
        """Fuzzy-match a predicted dish label to stored recipes.

        Returns the best-matching recipe dict or ``None``.
        """
        best_match = None
        best_score = 0.0

        dish_lower = dish_name.lower().replace("_", " ")
        for recipe in self.recipes:
            recipe_lower = recipe["name"].lower()
            score = SequenceMatcher(None, dish_lower, recipe_lower).ratio()
            if score > best_score:
                best_score = score
                best_match = recipe

        if best_score >= threshold:
            return {**best_match, "match_score": round(best_score, 2)}
        return None

    # ------------------------------------------------------------------
    # Ingredient-based recommendation
    # ------------------------------------------------------------------
    def recommend_by_ingredients(
        self, available_ingredients: List[str], top_k: int = 3
    ) -> List[Dict]:
        """Rank recipes by ingredient overlap with the user's available
        ingredients and return the top-k results.

        Score = matched_ingredients / total_ingredients_required
        """
        available_set = {ing.lower().strip() for ing in available_ingredients}
        scored: List[Tuple[float, Dict]] = []

        for recipe in self.recipes:
            required = {ing.lower() for ing in recipe["ingredients"]}
            matched = available_set & required
            score = len(matched) / len(required) if required else 0.0

            scored.append(
                (
                    score,
                    {
                        **recipe,
                        "score": round(score, 2),
                        "matched_ingredients": sorted(matched),
                        "missing_ingredients": sorted(required - available_set),
                    },
                )
            )

        # Sort by score descending, then by prep_time string length (proxy for speed)
        scored.sort(key=lambda x: (-x[0], len(x[1].get("prep_time", ""))))
        return [item[1] for item in scored[:top_k]]

    # ------------------------------------------------------------------
    # Missing-ingredient analysis
    # ------------------------------------------------------------------
    def get_missing_ingredients(
        self, recipe: Dict, available_ingredients: List[str]
    ) -> List[str]:
        """Return a list of ingredients required by *recipe* that are
        not in *available_ingredients*."""
        available_set = {ing.lower().strip() for ing in available_ingredients}
        required = {ing.lower() for ing in recipe["ingredients"]}
        return sorted(required - available_set)

    # ------------------------------------------------------------------
    # Substitution lookup
    # ------------------------------------------------------------------
    def get_substitutions(self, ingredient: str) -> Optional[Dict]:
        """Return substitution info for a given ingredient."""
        key = ingredient.lower().strip()
        if key in self.substitutions:
            return {
                "ingredient": key,
                **self.substitutions[key],
            }
        return None

    def get_all_substitutions_for_missing(
        self, missing: List[str]
    ) -> List[Dict]:
        """Return substitutions for every missing ingredient that has an
        entry in the substitutions database."""
        results = []
        for ing in missing:
            sub = self.get_substitutions(ing)
            if sub is not None:
                results.append(sub)
        return results

    # ------------------------------------------------------------------
    # Joint embedding-based retrieval
    # ------------------------------------------------------------------
    def find_by_joint_embedding(
        self, query: str, joint_embedder, top_k: int = 3
    ) -> List[Dict]:
        """Find recipes using joint text embedding (TF-IDF + SVD).

        Uses the pre-built joint embedder to find similar recipes by text query.
        Falls back to empty list if embedder is not available.

        Parameters
        ----------
        query : str
            Text query (dish name, ingredients, etc.)
        joint_embedder : JointEmbedder
            Pre-initialized joint embedder with recipe index built
        top_k : int
            Number of results to return

        Returns
        -------
        list[dict]
            Top-k recipes with similarity scores
        """
        if joint_embedder is None:
            return []

        results_with_scores = joint_embedder.find_by_query(query, top_k=top_k)
        recipes = []
        for recipe, score in results_with_scores:
            recipes.append({**recipe, "match_score": round(float(score), 2)})
        return recipes

    def find_by_image_features(
        self, features_2048, joint_embedder, top_k: int = 3
    ) -> List[Dict]:
        """Find recipes using ResNet50 image features aligned with text embeddings.

        Uses the joint embedder's vision projection to map image features into
        the shared text-image embedding space for recipe retrieval.

        Parameters
        ----------
        features_2048 : np.ndarray
            ResNet50 backbone features (2048-dim)
        joint_embedder : JointEmbedder
            Pre-initialized joint embedder with vision projection trained
        top_k : int
            Number of results to return

        Returns
        -------
        list[dict]
            Top-k recipes with similarity scores
        """
        if joint_embedder is None:
            return []

        results_with_scores = joint_embedder.find_by_image_features(
            features_2048, top_k=top_k
        )
        recipes = []
        for recipe, score in results_with_scores:
            recipes.append({**recipe, "match_score": round(float(score), 2)})
        return recipes

    # ------------------------------------------------------------------
    # Convenience / summary helpers
    # ------------------------------------------------------------------
    def get_all_recipe_names(self) -> List[str]:
        return [r["name"] for r in self.recipes]

    def get_quickest_recipe(self, recipes: List[Dict]) -> Optional[Dict]:
        """Return the recipe with the shortest prep time from a list."""
        def _parse_minutes(time_str: str) -> int:
            import re
            numbers = re.findall(r"\d+", time_str)
            return int(numbers[0]) if numbers else 999
        if not recipes:
            return None
        return min(recipes, key=lambda r: _parse_minutes(r.get("prep_time", "999")))


# ======================================================================
# Quick self-test
# ======================================================================
if __name__ == "__main__":
    engine = RecipeEngine()

    print("=== Dish lookup ===")
    result = engine.get_recipe_by_dish("spaghetti bolognese")
    if result:
        print(f"  Found: {result['name']} (match={result['match_score']})")

    print("\n=== Ingredient recommendation ===")
    recs = engine.recommend_by_ingredients(["egg", "rice", "onion", "pepper"])
    for r in recs:
        print(f"  {r['name']}  score={r['score']}  missing={r['missing_ingredients']}")

    print("\n=== Substitutions for 'egg' ===")
    sub = engine.get_substitutions("egg")
    if sub:
        print(f"  Alternatives: {sub['alternatives']}")
        print(f"  Notes: {sub['notes']}")
