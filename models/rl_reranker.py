"""
RL Reranker
===========
Loads user feedback and reranks recipe retrieval results based on
accumulated preferences.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict


class RLReranker:
    """Rerank recipes based on user feedback history."""

    def __init__(self, feedback_file: str = "data/feedback.jsonl"):
        """Initialize reranker and load feedback history.

        Parameters
        ----------
        feedback_file : str
            Path to newline-delimited JSON feedback file
        """
        self.feedback_file = Path(feedback_file)
        self.recipe_scores: Dict[str, float] = defaultdict(float)  # recipe_name -> avg_rating
        self.recipe_counts: Dict[str, int] = defaultdict(int)  # recipe_name -> count
        self.load_feedback()

    def load_feedback(self) -> None:
        """Load and parse feedback file."""
        if not self.feedback_file.exists():
            return

        try:
            with open(self.feedback_file, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    entry = json.loads(line)
                    if entry.get("type") == "recipe":
                        recipe_name = entry.get("recipe_name")
                        rating = entry.get("rating", 0)  # 1 or -1
                        if recipe_name:
                            self.recipe_scores[recipe_name] += rating
                            self.recipe_counts[recipe_name] += 1
        except Exception as e:
            print(f"[WARN] Failed to load feedback file: {e}")

    def get_recipe_score(self, recipe_name: str) -> float:
        """Get average feedback score for a recipe (-1 to 1 range).

        Parameters
        ----------
        recipe_name : str
            Recipe name

        Returns
        -------
        float
            Average score, or 0 if no feedback
        """
        if self.recipe_counts[recipe_name] == 0:
            return 0.0
        return self.recipe_scores[recipe_name] / self.recipe_counts[recipe_name]

    def rerank(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rerank recipes by blending original score with feedback score.

        Boosts recipes that users have rated positively, demotes those rated negatively.

        Parameters
        ----------
        results : list[dict]
            List of recipe dicts with 'name' and 'match_score' fields

        Returns
        -------
        list[dict]
            Reranked results, sorted by blended score descending
        """
        if not results:
            return results

        # Compute blended scores: 0.8 * original + 0.2 * feedback
        reranked = []
        for recipe in results:
            original_score = recipe.get("match_score", 0.0)
            feedback_score = self.get_recipe_score(recipe["name"])

            # Blend scores (feedback is -1 to 1, scale to impact 0.2 weight)
            blended = (0.8 * original_score) + (0.2 * (feedback_score + 1) / 2)
            recipe["blended_score"] = round(blended, 3)

            reranked.append(recipe)

        # Sort by blended score descending
        reranked.sort(key=lambda r: r["blended_score"], reverse=True)
        return reranked
