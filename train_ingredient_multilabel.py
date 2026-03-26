#!/usr/bin/env python3
"""
Train Multi-Label Ingredient Classifier on Pantry Images
=========================================================
Trains ResNet50 for multi-label ingredient detection using the same
architecture as models/ingredient_classifier.py.

Usage:
    python train_ingredient_multilabel.py

Output:
    - checkpoints/ingredient_classifier_best.pt (best model)
"""

import os
from pathlib import Path
from typing import List, Dict
import random

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision import transforms, models
from PIL import Image
from tqdm import tqdm

# ============================================================================
# Configuration
# ============================================================================

DATA_DIR = Path("data/pantry_images")
CHECKPOINT_DIR = Path("checkpoints")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

LEARNING_RATE = 5e-5
BATCH_SIZE = 16
NUM_EPOCHS = 30
PATIENCE = 5
IMG_SIZE = 224
TRAIN_SPLIT = 0.7
VAL_SPLIT = 0.15
TEST_SPLIT = 0.15

print(f"[INFO] Using device: {DEVICE}")
print(f"[INFO] GPU available: {torch.cuda.is_available()}")

# ============================================================================
# Dataset
# ============================================================================

class MultiLabelPantryDataset(Dataset):
    """Multi-label ingredient dataset (images can have multiple ingredients)."""

    def __init__(self, root_dir: Path, image_to_labels: Dict[str, List[int]], transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.image_to_labels = image_to_labels

        # Get all ingredient classes
        self.classes = sorted([
            d.name for d in root_dir.iterdir()
            if d.is_dir() and d.name != "__pycache__"
        ])
        self.class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
        print(f"[OK] Found {len(self.classes)} ingredient classes")

        # Build image list (all images)
        self.images = []
        for img_path in image_to_labels.keys():
            self.images.append(img_path)

        print(f"[OK] Loaded {len(self.images)} total images")

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = self.images[idx]
        try:
            image = Image.open(img_path).convert("RGB")
            if self.transform:
                image = self.transform(image)

            # Get multi-label target (one-hot encoded)
            labels = torch.zeros(len(self.classes), dtype=torch.float32)
            for label_idx in self.image_to_labels[img_path]:
                labels[label_idx] = 1.0

            return image, labels
        except Exception as e:
            print(f"[WARN] Failed to load {img_path}: {e}")
            return torch.zeros(3, IMG_SIZE, IMG_SIZE), torch.zeros(len(self.classes), dtype=torch.float32)


# ============================================================================
# Model (matches models/ingredient_classifier.py)
# ============================================================================

class IngredientClassifierMultiLabel(nn.Module):
    """ResNet50-based multi-label ingredient classifier."""

    def __init__(self, num_classes: int):
        super().__init__()
        self.backbone = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)

        # Freeze early layers
        for param in list(self.backbone.parameters())[:-30]:
            param.requires_grad = False

        # Replace final FC layer with multi-label head
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(p=0.3),
            nn.Linear(in_features, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.2),
            nn.Linear(512, num_classes),
        )

    def forward(self, x):
        return self.backbone(x)


# ============================================================================
# Training
# ============================================================================

def train_epoch(model, dataloader, optimizer, criterion, device):
    """Train for one epoch."""
    model.train()
    total_loss = 0
    total = 0

    pbar = tqdm(dataloader, desc="Training", leave=False)
    for images, labels in pbar:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)  # Raw logits
        loss = criterion(outputs, labels)  # BCEWithLogitsLoss
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * labels.size(0)
        total += labels.size(0)

        pbar.set_postfix(loss=f"{loss.item():.4f}")

    return total_loss / total if total > 0 else 0


def evaluate(model, dataloader, criterion, device):
    """Evaluate on a dataset."""
    model.eval()
    total_loss = 0
    total = 0
    mAP = 0  # Mean Average Precision

    with torch.no_grad():
        for images, labels in tqdm(dataloader, desc="Evaluating", leave=False):
            images, labels = images.to(device), labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            total_loss += loss.item() * labels.size(0)
            total += labels.size(0)

            # Simple accuracy: all predictions correct for sample
            probs = torch.sigmoid(outputs)
            predicted = (probs > 0.5).float()
            correct = (predicted == labels).all(dim=1).sum().item()
            mAP += correct

    return total_loss / total if total > 0 else 0, mAP / total if total > 0 else 0


def main():
    CHECKPOINT_DIR.mkdir(exist_ok=True)

    # ========================================================================
    # Data
    # ========================================================================
    print("[*] Loading pantry dataset...")

    # Build image-to-labels mapping (single-label: each image is one ingredient)
    image_to_labels = {}
    classes = sorted([d.name for d in DATA_DIR.iterdir() if d.is_dir() and d.name != "__pycache__"])
    for cls_idx, cls_name in enumerate(classes):
        cls_dir = DATA_DIR / cls_name
        for img_file in cls_dir.glob("*.jpg"):
            # For now, assume single-label (image path → [class_idx])
            # Can be extended to multi-label if you have multi-ingredient images
            image_to_labels[str(img_file)] = [cls_idx]

    print(f"[OK] Built mapping for {len(image_to_labels)} images")

    transform_train = transforms.Compose([
        transforms.RandomResizedCrop(IMG_SIZE, scale=(0.7, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    transform_val = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    # Create full dataset
    all_images = list(image_to_labels.keys())
    random.shuffle(all_images)

    train_size = int(len(all_images) * TRAIN_SPLIT)
    val_size = int(len(all_images) * VAL_SPLIT)

    train_images = all_images[:train_size]
    val_images = all_images[train_size:train_size + val_size]
    test_images = all_images[train_size + val_size:]

    train_labels = {img: image_to_labels[img] for img in train_images}
    val_labels = {img: image_to_labels[img] for img in val_images}
    test_labels = {img: image_to_labels[img] for img in test_images}

    train_dataset = MultiLabelPantryDataset(DATA_DIR, train_labels, transform_train)
    val_dataset = MultiLabelPantryDataset(DATA_DIR, val_labels, transform_val)
    test_dataset = MultiLabelPantryDataset(DATA_DIR, test_labels, transform_val)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=4)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=4)

    print(f"[OK] Train: {len(train_images)}, Val: {len(val_images)}, Test: {len(test_images)}")

    # ========================================================================
    # Model
    # ========================================================================
    print("[*] Building multi-label model...")
    num_classes = len(train_dataset.classes)
    model = IngredientClassifierMultiLabel(num_classes).to(DEVICE)
    optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE)
    criterion = nn.BCEWithLogitsLoss()  # Multi-label loss
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=NUM_EPOCHS)

    best_val_acc = 0
    patience_counter = 0

    # ========================================================================
    # Training Loop
    # ========================================================================
    print("[*] Starting training...")
    for epoch in range(NUM_EPOCHS):
        print(f"\n[Epoch {epoch+1}/{NUM_EPOCHS}]")

        train_loss = train_epoch(model, train_loader, optimizer, criterion, DEVICE)
        val_loss, val_acc = evaluate(model, val_loader, criterion, DEVICE)
        scheduler.step()

        print(f"  Train Loss: {train_loss:.4f}")
        print(f"  Val Loss:   {val_loss:.4f} | Val Acc: {val_acc:.4f}")

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            checkpoint_path = CHECKPOINT_DIR / "ingredient_classifier_best.pt"
            torch.save(model.state_dict(), checkpoint_path)
            print(f"  [SAVE] Best model saved (val_acc: {val_acc:.4f})")
        else:
            patience_counter += 1
            if patience_counter >= PATIENCE:
                print(f"[STOP] Early stopping after {epoch+1} epochs")
                break

    # ========================================================================
    # Test Evaluation
    # ========================================================================
    print("\n[*] Evaluating on test set...")
    test_loss, test_acc = evaluate(model, test_loader, criterion, DEVICE)
    print(f"[FINAL] Test Loss: {test_loss:.4f} | Test Acc: {test_acc:.4f}")

    print(f"\n[DONE] Training complete!")
    print(f"[INFO] Checkpoint: {CHECKPOINT_DIR / 'ingredient_classifier_best.pt'}")
    print(f"[INFO] Best validation accuracy: {best_val_acc:.4f}")
    print(f"[INFO] Test accuracy: {test_acc:.4f}")


if __name__ == "__main__":
    main()
