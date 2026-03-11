"""
Ingredient Recognition Model
=============================
Multi-label classifier built on ResNet50 for detecting pantry
ingredients from images.  Uses sigmoid activation and Binary
Cross-Entropy loss for multi-label prediction.

Usage
-----
    from models.ingredient_classifier import IngredientClassifier

    clf = IngredientClassifier()
    clf.load_pretrained()
    detected = clf.predict(pil_image, threshold=0.5)
    # {'egg': 0.92, 'onion': 0.87, 'rice': 0.79}
"""

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from typing import Dict, List, Optional, Tuple

# ------------------------------------------------------------------
# Ingredient classes (11 classes as specified)
# ------------------------------------------------------------------
INGREDIENT_CLASSES: List[str] = [
    "onion", "tomato", "garlic", "milk", "pepper", "potato",
    "apple", "avocado", "banana", "kiwi", "lemon", "lime", "mango", "melon", "orange", "pear", "pineapple",
    "plum", "pomegranate", "asparagus", "aubergine", "cabbage", "carrot", "cucumber", "ginger", "leek",
    "mushroom", "zucchini"
]


class IngredientClassifier(nn.Module):
    """ResNet50-based multi-label ingredient classifier.

    Parameters
    ----------
    num_classes : int
        Number of ingredient categories.
    class_names : list[str] | None
        Human-readable labels for each class index.
    pretrained_backbone : bool
        Whether to initialise the ResNet50 backbone with ImageNet weights.
    """

    def __init__(
        self,
        num_classes: int = 28,
        class_names: Optional[List[str]] = None,
        pretrained_backbone: bool = True,
    ):
        super().__init__()
        self.num_classes = num_classes
        self.class_names = class_names or INGREDIENT_CLASSES[:num_classes]

        # Build backbone
        weights = models.ResNet50_Weights.DEFAULT if pretrained_backbone else None
        self.backbone = models.resnet50(weights=weights)

        # Replace final FC layer with multi-label head (no softmax — sigmoid applied later)
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(in_features, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.2),
            nn.Linear(512, num_classes),
        )

    # ------------------------------------------------------------------
    # Forward pass
    # ------------------------------------------------------------------
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass returning raw logits (before sigmoid)."""
        return self.backbone(x)

    # ------------------------------------------------------------------
    # Pretrained loading
    # ------------------------------------------------------------------
    def load_pretrained(self, checkpoint_path: Optional[str] = None):
        """Load a trained checkpoint."""
        if checkpoint_path:
            state = torch.load(checkpoint_path, map_location="cpu")
            self.load_state_dict(state)
        self.eval()
        return self

    # ------------------------------------------------------------------
    # Multi-label prediction
    # ------------------------------------------------------------------
    @torch.no_grad()
    def predict(
        self, image: Image.Image, threshold: float = 0.5
    ) -> Dict[str, float]:
        """Predict ingredient presence from a PIL Image.

        Returns a dict of ``{ingredient_name: confidence}`` for all
        ingredients whose sigmoid probability exceeds *threshold*.
        """
        tensor = self.get_transforms()(image).unsqueeze(0)
        logits = self.forward(tensor)
        probs = torch.sigmoid(logits).squeeze()

        detected = {}
        for idx, prob in enumerate(probs):
            if prob.item() >= threshold:
                label = (
                    self.class_names[idx]
                    if idx < len(self.class_names)
                    else f"ingredient_{idx}"
                )
                detected[label] = round(prob.item(), 2)

        # Sort by confidence descending
        return dict(sorted(detected.items(), key=lambda x: -x[1]))

    @torch.no_grad()
    def predict_all(self, image: Image.Image) -> Dict[str, float]:
        """Return probabilities for ALL ingredient classes (no threshold)."""
        tensor = self.get_transforms()(image).unsqueeze(0)
        logits = self.forward(tensor)
        probs = torch.sigmoid(logits).squeeze()

        result = {}
        for idx, prob in enumerate(probs):
            label = (
                self.class_names[idx]
                if idx < len(self.class_names)
                else f"ingredient_{idx}"
            )
            result[label] = round(prob.item(), 2)
        return dict(sorted(result.items(), key=lambda x: -x[1]))

    # ------------------------------------------------------------------
    # Image transforms
    # ------------------------------------------------------------------
    @staticmethod
    def get_transforms(train: bool = False) -> transforms.Compose:
        """Return image transform pipeline."""
        if train:
            return transforms.Compose(
                [
                    transforms.RandomResizedCrop(224, scale=(0.7, 1.0)),
                    transforms.RandomHorizontalFlip(),
                    transforms.RandomVerticalFlip(p=0.2),
                    transforms.RandomRotation(30),
                    transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
                    transforms.RandomPerspective(distortion_scale=0.2, p=0.4),
                    transforms.ColorJitter(
                        brightness=0.4, contrast=0.4, saturation=0.4, hue=0.1
                    ),
                    transforms.RandomGrayscale(p=0.1),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225],
                    ),
                ]
            )
        return transforms.Compose(
            [
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
            ]
        )

    # ------------------------------------------------------------------
    # Loss function
    # ------------------------------------------------------------------
    @staticmethod
    def get_loss_fn(pos_weight: Optional[torch.Tensor] = None) -> nn.Module:
        """Return BCEWithLogitsLoss for multi-label training.
        
        Optional `pos_weight` helps handle class imbalance (e.g. fewer
        images for some ingredients).
        """
        return nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    # ------------------------------------------------------------------
    # Freeze / unfreeze helpers
    # ------------------------------------------------------------------
    def freeze_backbone(self):
        for name, param in self.backbone.named_parameters():
            if "fc" not in name:
                param.requires_grad = False

    def unfreeze_backbone(self):
        for param in self.backbone.parameters():
            param.requires_grad = True


# ======================================================================
# Quick self-test
# ======================================================================
if __name__ == "__main__":
    model = IngredientClassifier(num_classes=11, pretrained_backbone=False)
    print(f"Model created with {model.num_classes} classes: {model.class_names}")

    # Dummy prediction
    dummy_img = Image.new("RGB", (256, 256), color="green")
    all_preds = model.predict_all(dummy_img)
    print("\nAll predictions:")
    for name, prob in all_preds.items():
        print(f"  {name}: {prob:.2f}")

    detected = model.predict(dummy_img, threshold=0.5)
    print(f"\nDetected (threshold=0.5): {detected}")
