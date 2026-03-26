"""
Ingredient Recognition Model (CLIP-based Zero-Shot)
===================================================
Multi-label ingredient classifier using CLIP's zero-shot capabilities.
No training required — detects any ingredient by comparing image features
to ingredient text embeddings.

Usage
-----
    from models.ingredient_classifier import IngredientClassifier

    clf = IngredientClassifier()
    detected = clf.predict(pil_image, threshold=0.25)
    # {'apple': 0.82, 'tomato': 0.71, 'garlic': 0.65}
"""

import torch
import clip
from PIL import Image
from typing import Dict, List, Optional
import numpy as np

# ------------------------------------------------------------------
# Ingredient classes
# ------------------------------------------------------------------
INGREDIENT_CLASSES: List[str] = [
    "onion", "tomato", "garlic", "milk", "pepper", "potato",
    "apple", "avocado", "banana", "kiwi", "lemon", "lime", "mango", "melon", "orange", "pear", "pineapple",
    "plum", "pomegranate", "asparagus", "aubergine", "cabbage", "carrot", "cucumber", "ginger", "leek",
    "mushroom", "zucchini"
]


class IngredientClassifier:
    """CLIP-based zero-shot multi-label ingredient classifier.

    Uses CLIP's vision and text encoders to detect ingredients without training.
    Each ingredient is treated as a class to zero-shot classify.

    Parameters
    ----------
    num_classes : int
        Number of ingredient categories (default: 28).
    class_names : list[str] | None
        Human-readable labels for each class index.
    model_name : str
        CLIP model variant (default: "ViT-L/14").
    """

    def __init__(
        self,
        num_classes: int = 28,
        class_names: Optional[List[str]] = None,
        model_name: str = "ViT-L/14",
    ):
        self.num_classes = num_classes
        self.class_names = class_names or INGREDIENT_CLASSES[:num_classes]
        self.model_name = model_name

        # Detect device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load CLIP model
        self.model, self.preprocess = clip.load(model_name, device=self.device)
        self.model.eval()

        # Pre-encode all ingredient names for efficiency
        self._encode_ingredients()

    def _encode_ingredients(self) -> None:
        """Pre-compute text embeddings for all ingredient classes."""
        with torch.no_grad():
            # Prepare text prompts: "a photo of {ingredient}"
            texts = [f"a photo of {ing}" for ing in self.class_names]
            text_tokens = clip.tokenize(texts).to(self.device)
            self.ingredient_embeddings = self.model.encode_text(text_tokens)
            self.ingredient_embeddings /= self.ingredient_embeddings.norm(dim=-1, keepdim=True)

    def predict(
        self,
        image: Image.Image,
        threshold: float = 0.25,
    ) -> Dict[str, float]:
        """Predict ingredient presence from a PIL Image.

        Returns a dict of {ingredient_name: confidence} for all
        ingredients whose similarity score exceeds *threshold*.

        Parameters
        ----------
        image : PIL.Image
            Input image
        threshold : float
            Confidence threshold (0-1). Lower = more detections.
            Default 0.25 works well for multi-label detection.

        Returns
        -------
        dict
            {ingredient_name: confidence}, sorted by confidence descending
        """
        with torch.no_grad():
            # Preprocess and encode image
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            image_features = self.model.encode_image(image_tensor)
            image_features /= image_features.norm(dim=-1, keepdim=True)

            # Compute similarity with all ingredients
            logits = (image_features @ self.ingredient_embeddings.t()).squeeze()
            scores = torch.sigmoid(logits).cpu().numpy()

        # Extract detected ingredients
        detected = {}
        for idx, score in enumerate(scores):
            if score >= threshold:
                detected[self.class_names[idx]] = round(float(score), 2)

        # Sort by confidence descending
        return dict(sorted(detected.items(), key=lambda x: -x[1]))

    def predict_all(self, image: Image.Image) -> Dict[str, float]:
        """Return confidence scores for ALL ingredient classes (no threshold).

        Parameters
        ----------
        image : PIL.Image
            Input image

        Returns
        -------
        dict
            {ingredient_name: confidence} for all classes, sorted descending
        """
        with torch.no_grad():
            # Preprocess and encode image
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            image_features = self.model.encode_image(image_tensor)
            image_features /= image_features.norm(dim=-1, keepdim=True)

            # Compute similarity with all ingredients
            logits = (image_features @ self.ingredient_embeddings.t()).squeeze()
            scores = torch.sigmoid(logits).cpu().numpy()

        # All ingredients with scores
        result = {}
        for idx, score in enumerate(scores):
            result[self.class_names[idx]] = round(float(score), 2)

        return dict(sorted(result.items(), key=lambda x: -x[1]))

    # Compatibility methods (for API compatibility, no-ops)
    def load_pretrained(self, checkpoint_path: Optional[str] = None):
        """No-op for API compatibility (CLIP is zero-shot, no checkpoint needed)."""
        return self

    def eval(self):
        """Set to eval mode."""
        self.model.eval()
        return self


# ======================================================================
# Quick self-test
# ======================================================================
if __name__ == "__main__":
    from PIL import Image
    import urllib.request

    print("Loading CLIP ingredient classifier...")
    clf = IngredientClassifier(num_classes=28)

    # Test with a real apple image
    print("\nDownloading test apple image...")
    try:
        url = "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=500&h=500&fit=crop"
        urllib.request.urlretrieve(url, "/tmp/apple.jpg")
        img = Image.open("/tmp/apple.jpg")

        print("\nPredicting ingredients (threshold=0.25):")
        detected = clf.predict(img, threshold=0.25)
        for ing, score in list(detected.items())[:5]:
            print(f"  {ing}: {score:.2f}")

        print("\nAll ingredients (top 10):")
        all_preds = clf.predict_all(img)
        for ing, score in list(all_preds.items())[:10]:
            print(f"  {ing}: {score:.2f}")
    except Exception as e:
        print(f"Error during test: {e}")
