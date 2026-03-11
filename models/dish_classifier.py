"""
Dish Classification Model
=========================
Transfer-learning classifier built on ResNet50 for recognising prepared
dishes from the Food-101 dataset (or a user-defined subset of classes).

Usage
-----
    from models.dish_classifier import DishClassifier

    clf = DishClassifier(num_classes=10)
    clf.load_pretrained()            # ImageNet weights + custom head
    label, confidence = clf.predict(pil_image)
"""

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from typing import List, Tuple, Optional, Dict

# ------------------------------------------------------------------
# Default Food-101 subset (10 representative classes)
# ------------------------------------------------------------------
DEFAULT_CLASSES: List[str] = [
    "apple_pie",
    "baby_back_ribs",
    "baklava",
    "beef_carpaccio",
    "beef_tartare",
    "beet_salad",
    "beignets",
    "bibimbap",
    "bread_pudding",
    "breakfast_burrito",
    "bruschetta",
    "caesar_salad",
    "cannoli",
    "caprese_salad",
    "carrot_cake",
    "ceviche",
    "cheesecake",
    "cheese_plate",
    "chicken_curry",
    "chicken_quesadilla",
]


class DishClassifier(nn.Module):
    """ResNet50-based food dish classifier.

    Parameters
    ----------
    num_classes : int
        Number of dish categories.
    class_names : list[str] | None
        Human-readable labels for each class index.
    pretrained_backbone : bool
        Whether to initialise the ResNet50 backbone with ImageNet weights.
    """

    def __init__(
        self,
        num_classes: int = 10,
        class_names: Optional[List[str]] = None,
        pretrained_backbone: bool = True,
    ):
        super().__init__()
        self.num_classes = num_classes
        self.class_names = class_names or DEFAULT_CLASSES[:num_classes]

        # Build backbone
        weights = models.ResNet50_Weights.DEFAULT if pretrained_backbone else None
        self.backbone = models.resnet50(weights=weights)

        # Replace final FC layer
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
        """Standard forward pass returning raw logits."""
        return self.backbone(x)

    # ------------------------------------------------------------------
    # Pretrained loading
    # ------------------------------------------------------------------
    def load_pretrained(self, checkpoint_path: Optional[str] = None):
        """Load a trained checkpoint.  If no path is given, the model
        keeps its ImageNet-initialised backbone + random head."""
        if checkpoint_path:
            state = torch.load(checkpoint_path, map_location="cpu")
            self.load_state_dict(state)
        self.eval()
        return self

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------
    @torch.no_grad()
    def predict(
        self, image: Image.Image, top_k: int = 3
    ) -> List[Tuple[str, float]]:
        """Predict top-k dish labels from a PIL Image.

        Returns a list of ``(label, confidence)`` tuples sorted by
        descending confidence.
        """
        tensor = self.get_transforms()(image).unsqueeze(0)
        logits = self.forward(tensor)
        probs = torch.softmax(logits, dim=1).squeeze()

        top_probs, top_indices = probs.topk(min(top_k, self.num_classes))
        results = []
        for prob, idx in zip(top_probs, top_indices):
            label = (
                self.class_names[idx.item()]
                if idx.item() < len(self.class_names)
                else f"class_{idx.item()}"
            )
            results.append((label.replace("_", " ").title(), prob.item()))
        return results

    # ------------------------------------------------------------------
    # Image transforms
    # ------------------------------------------------------------------
    @staticmethod
    def get_transforms(train: bool = False) -> transforms.Compose:
        """Return image transform pipeline for training or inference."""
        if train:
            return transforms.Compose(
                [
                    transforms.RandomResizedCrop(224),
                    transforms.RandomHorizontalFlip(),
                    transforms.RandomRotation(15),
                    transforms.ColorJitter(
                        brightness=0.2, contrast=0.2, saturation=0.2
                    ),
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
    # Freeze / unfreeze helpers (for fine-tuning)
    # ------------------------------------------------------------------
    def freeze_backbone(self):
        """Freeze all backbone parameters except the custom head."""
        for name, param in self.backbone.named_parameters():
            if "fc" not in name:
                param.requires_grad = False

    def unfreeze_backbone(self):
        """Unfreeze the full backbone for fine-tuning."""
        for param in self.backbone.parameters():
            param.requires_grad = True


# ======================================================================
# Quick self-test
# ======================================================================
if __name__ == "__main__":
    model = DishClassifier(num_classes=10, pretrained_backbone=False)
    print(f"Model created with {model.num_classes} classes: {model.class_names}")

    # Dummy prediction
    dummy_img = Image.new("RGB", (256, 256), color="red")
    preds = model.predict(dummy_img, top_k=3)
    for label, conf in preds:
        print(f"  {label}: {conf:.4f}")
