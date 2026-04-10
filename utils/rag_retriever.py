"""
RAG (Retrieval-Augmented Generation) Retriever
==============================================
Dynamically retrieves relevant recipes per question using joint embeddings,
then augments the assistant context before answering.
Optionally reranks results based on user feedback via RL reranker.
"""

from typing import Dict, Any, List, Tuple, Optional


class RAGRetriever:
    """Retrieve relevant recipes to augment assistant context."""

    @staticmethod
    def retrieve(
        question: str,
        context: Dict[str, Any],
        embedder,
        engine,
        reranker=None,
        top_k: int = 3,
    ) -> Dict[str, Any]:
        """Retrieve top-k recipes by semantic similarity to the question.

        Attempts both text-based and ingredient-based retrieval, then merges
        and deduplicates by recipe name, keeping the highest score.
        Optionally reranks results using RL feedback if reranker is provided.

        Parameters
        ----------
        question : str
            User's free-text question
        context : dict
            Current context (may include detected_ingredients, etc.)
        embedder : JointEmbedder
            Pre-initialized joint embedder with recipe index
        engine : RecipeEngine
            Recipe engine for ingredient-based recommendations
        reranker : RLReranker, optional
            Reranker to boost recipes based on user feedback
        top_k : int
            Number of recipes to retrieve

        Returns
        -------
        dict
            Augmented context with updated 'recipes' list
        """
        if embedder is None or engine is None:
            return context

        # Start with a copy of the original context
        augmented = dict(context)

        retrieved_recipes: Dict[str, Tuple[Dict[str, Any], float]] = {}

        # Semantic text search using joint embeddings
        text_results = engine.find_by_joint_embedding(
            question, embedder, top_k=top_k
        )
        for recipe in text_results:
            score = recipe.get("match_score", 0.0)
            recipe_name = recipe["name"]
            if recipe_name not in retrieved_recipes or score > retrieved_recipes[recipe_name][1]:
                retrieved_recipes[recipe_name] = (recipe, score)

        # If user has detected ingredients, also do ingredient-based retrieval
        detected_ingredients = context.get("detected_ingredients", {})
        if detected_ingredients:
            ing_list = list(detected_ingredients.keys()) if isinstance(detected_ingredients, dict) else detected_ingredients
            if ing_list:
                ingredient_results = engine.recommend_by_ingredients(ing_list, top_k=top_k)
                for recipe in ingredient_results:
                    score = recipe.get("score", 0.0)
                    recipe_name = recipe["name"]
                    if recipe_name not in retrieved_recipes or score > retrieved_recipes[recipe_name][1]:
                        retrieved_recipes[recipe_name] = (recipe, score)

        # Sort by score descending, take top-k
        sorted_recipes = sorted(
            retrieved_recipes.values(),
            key=lambda x: x[1],
            reverse=True,
        )[:top_k]

        # Extract just the recipe dicts
        final_recipes = [recipe for recipe, _ in sorted_recipes]

        # Apply RL reranking if available (boost liked recipes based on user feedback)
        if final_recipes and reranker is not None:
            try:
                final_recipes = reranker.rerank(final_recipes)
            except Exception as e:
                # If reranking fails, continue with original ranking
                print(f"[WARN] RL reranking failed: {e}")

        # Augment context with retrieved recipes
        if final_recipes:
            augmented["recipes"] = final_recipes

        return augmented
