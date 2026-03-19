"""
Joint Vision-Text Embedder
===========================
Aligns ResNet50 image features with recipe text embeddings (TF-IDF) in a shared space.
This creates a genuine joint embedding for recipe retrieval that's more accurate than
fuzzy string matching.

Architecture:
- Text side: Recipe name + ingredients → TF-IDF → SVD projection (128-dim)
- Vision side: ResNet50 2048-dim features → Linear projection (128-dim)
- Both spaces: Cosine similarity for retrieval
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import pickle
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.linear_model import Ridge


class JointEmbedder:
    """Enables recipe retrieval via aligned image and text embeddings."""

    def __init__(self, embedding_dim: int = 128):
        """
        Parameters
        ----------
        embedding_dim : int
            Dimension of the joint embedding space (default 128)
        """
        self.embedding_dim = embedding_dim
        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self.text_svd: Optional[TruncatedSVD] = None
        self.img_projection: Optional[Ridge] = None
        self.recipe_embeddings: Optional[np.ndarray] = None
        self.recipe_texts: Optional[List[str]] = None
        self.recipes: Optional[List[Dict]] = None

    def build_recipe_index(self, recipes: List[Dict[str, Any]]) -> None:
        """
        Build TF-IDF index over all recipes for text-based retrieval.

        Parameters
        ----------
        recipes : list[dict]
            List of recipe dicts with keys: 'name', 'ingredients', etc.
        """
        self.recipes = recipes

        # Combine recipe name and ingredients into single text for each recipe
        texts = []
        for recipe in recipes:
            name = recipe.get("name", "")
            ingredients = " ".join(recipe.get("ingredients", []))
            combined = f"{name} {ingredients}"
            texts.append(combined)

        self.recipe_texts = texts

        # TF-IDF vectorization
        self.tfidf_vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=1000,
            lowercase=True,
            stop_words="english",
        )
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)

        # SVD projection to embedding_dim
        self.text_svd = TruncatedSVD(n_components=self.embedding_dim, random_state=42)
        self.recipe_embeddings = self.text_svd.fit_transform(tfidf_matrix)

        print(
            f"[JointEmbedder] Indexed {len(recipes)} recipes in {self.embedding_dim}-dim space."
        )

    def find_by_query(
        self, text_query: str, top_k: int = 3
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Find top-k recipes by text query (dish name, ingredients, etc.)

        Parameters
        ----------
        text_query : str
            Query text (e.g., "spaghetti bolognese" or "pasta with tomato")
        top_k : int
            Number of results to return

        Returns
        -------
        list[tuple[dict, float]]
            List of (recipe, similarity_score) tuples, sorted by similarity (descending)
        """
        if self.recipe_embeddings is None:
            return []

        # Encode query via same pipeline as recipes
        query_tfidf = self.tfidf_vectorizer.transform([text_query])
        query_embedding = self.text_svd.transform(query_tfidf)[0]  # shape: (embedding_dim,)

        # Cosine similarity vs all recipes
        similarities = cosine_similarity(
            [query_embedding], self.recipe_embeddings
        )[0]

        # Top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            if 0 <= idx < len(self.recipes):
                results.append((self.recipes[idx], float(similarities[idx])))

        return results

    def find_by_image_features(
        self, features_2048: np.ndarray, top_k: int = 3
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Find top-k recipes by ResNet50 image features (2048-dim).

        Uses a learned projection (Ridge regression) from vision to text space.

        Parameters
        ----------
        features_2048 : np.ndarray
            ResNet50 backbone output, shape (2048,) or (batch, 2048)
        top_k : int
            Number of results to return

        Returns
        -------
        list[tuple[dict, float]]
            List of (recipe, similarity_score) tuples
        """
        if self.recipe_embeddings is None or self.img_projection is None:
            return []

        # Ensure 1D input
        if features_2048.ndim == 2:
            features_2048 = features_2048[0]

        # Project 2048-dim → embedding_dim
        img_embedding = self.img_projection.predict([features_2048])[0]

        # Cosine similarity vs all recipes
        similarities = cosine_similarity(
            [img_embedding], self.recipe_embeddings
        )[0]

        # Top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            if 0 <= idx < len(self.recipes):
                results.append((self.recipes[idx], float(similarities[idx])))

        return results

    def train_vision_projection(
        self, class_names: List[str], class_features: np.ndarray
    ) -> None:
        """
        Train the vision → text projection using dish class labels.

        For each dish class (e.g., "Spaghetti Bolognese"), we have:
        - Class name encoded as TF-IDF + SVD → target embedding
        - Class feature vector (2048-dim) → input

        This learns a linear bridge from vision to text space.

        Parameters
        ----------
        class_names : list[str]
            List of dish class names (e.g., ["baby back ribs", "apple pie", ...])
        class_features : np.ndarray
            Array of shape (num_classes, 2048) with ResNet50 features per class
        """
        if self.text_svd is None:
            print("[WARN] Cannot train vision projection: text embeddings not built yet.")
            return

        # Encode class names via same pipeline
        class_tfidf = self.tfidf_vectorizer.transform(class_names)
        target_embeddings = self.text_svd.transform(class_tfidf)  # (num_classes, embedding_dim)

        # Ridge regression: 2048-dim → embedding_dim
        self.img_projection = Ridge(alpha=1.0, random_state=42)
        self.img_projection.fit(class_features, target_embeddings)

        print(
            f"[JointEmbedder] Trained vision projection on {len(class_names)} classes."
        )

    def save(self, path: str) -> None:
        """Pickle the embedder state for fast reload."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        state = {
            "embedding_dim": self.embedding_dim,
            "tfidf_vectorizer": self.tfidf_vectorizer,
            "text_svd": self.text_svd,
            "img_projection": self.img_projection,
            "recipe_embeddings": self.recipe_embeddings,
            "recipe_texts": self.recipe_texts,
            "recipes": self.recipes,
        }

        with open(path, "wb") as f:
            pickle.dump(state, f)

        print(f"[JointEmbedder] Saved to {path}")

    @classmethod
    def load(cls, path: str) -> "JointEmbedder":
        """Load a previously saved embedder."""
        with open(path, "rb") as f:
            state = pickle.load(f)

        embedder = cls(embedding_dim=state["embedding_dim"])
        embedder.tfidf_vectorizer = state["tfidf_vectorizer"]
        embedder.text_svd = state["text_svd"]
        embedder.img_projection = state["img_projection"]
        embedder.recipe_embeddings = state["recipe_embeddings"]
        embedder.recipe_texts = state["recipe_texts"]
        embedder.recipes = state["recipes"]

        print(f"[JointEmbedder] Loaded from {path}")
        return embedder


if __name__ == "__main__":
    # Quick test
    from utils.recipe_engine import RecipeEngine

    # Load recipes
    engine = RecipeEngine()
    recipes = engine.recipes  # Loaded from data/recipes.json

    # Build embedder
    embedder = JointEmbedder(embedding_dim=128)
    embedder.build_recipe_index(recipes)

    # Test text-based retrieval
    results = embedder.find_by_query("spaghetti pasta tomato", top_k=3)
    print("\nText query results for 'spaghetti pasta tomato':")
    for recipe, score in results:
        print(f"  {recipe['name']:30s} (score: {score:.3f})")

    # Test image feature retrieval (dummy features for demo)
    dummy_features = np.random.randn(2048)
    if embedder.img_projection is not None:
        results = embedder.find_by_image_features(dummy_features, top_k=3)
        print("\nImage feature query results (dummy):")
        for recipe, score in results:
            print(f"  {recipe['name']:30s} (score: {score:.3f})")
    else:
        print("\n[Note] Vision projection not trained. Train via train_vision_projection().")
