"""
Train Ingredient Classifier on Pantry Images
=============================================
Fine-tunes ResNet50 on your pantry images for accurate ingredient detection.

Usage:
    python train_pantry_classifier.py

Output:
    - checkpoints/ingredient_classifier_best.pt (best model)
    - Logs training progress with validation metrics
"""

import os
from pathlib import Path
from typing import List, Tuple

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
BATCH_SIZE = 32
NUM_EPOCHS = 20
PATIENCE = 5  # Early stopping patience
IMG_SIZE = 224
TRAIN_SPLIT = 0.7
VAL_SPLIT = 0.15
TEST_SPLIT = 0.15

print(f"[INFO] Using device: {DEVICE}")
print(f"[INFO] GPU available: {torch.cuda.is_available()}")

# ============================================================================
# Dataset
# ============================================================================

class PantryDataset(Dataset):
    """Load pantry ingredient images."""

    def __init__(self, root_dir: Path, transform=None):
        self.root_dir = root_dir
        self.transform = transform

        # Get all ingredient classes (skip pantry_labels.csv)
        self.classes = sorted([
            d.name for d in root_dir.iterdir()
            if d.is_dir() and d.name != "__pycache__"
        ])
        self.class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
        print(f"[OK] Found {len(self.classes)} ingredient classes")

        # Build image list
        self.images = []
        for cls_name, cls_idx in self.class_to_idx.items():
            cls_dir = root_dir / cls_name
            img_files = list(cls_dir.glob("*.jpg"))

            for img_file in img_files:
                self.images.append((str(img_file), cls_idx))

        print(f"[OK] Loaded {len(self.images)} total images")

        # Show class distribution
        print("\n[Dataset Distribution]")
        for cls_name, cls_idx in self.class_to_idx.items():
            count = sum(1 for _, idx in self.images if idx == cls_idx)
            print(f"  {cls_name:15} : {count:4} images")

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path, label = self.images[idx]
        try:
            image = Image.open(img_path).convert("RGB")
            if self.transform:
                image = self.transform(image)
            return image, label
        except Exception as e:
            print(f"[WARN] Failed to load {img_path}: {e}")
            return torch.zeros(3, IMG_SIZE, IMG_SIZE), -1

# ============================================================================
# Model
# ============================================================================

class IngredientClassifierPantry(nn.Module):
    """ResNet50 classifier fine-tuned on pantry images."""

    def __init__(self, num_classes: int):
        super().__init__()
        self.backbone = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)

        # Freeze early layers, only fine-tune later layers
        for param in list(self.backbone.parameters())[:-30]:
            param.requires_grad = False

        # Replace final FC layer
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
    correct = 0
    total = 0

    pbar = tqdm(dataloader, desc="Training", leave=False)
    for images, labels in pbar:
        images, labels = images.to(device), labels.to(device)

        # Skip batches with invalid labels
        valid_mask = labels >= 0
        if valid_mask.sum() == 0:
            continue

        images = images[valid_mask]
        labels = labels[valid_mask]

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * labels.size(0)
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += labels.size(0)

        pbar.set_postfix(loss=f"{loss.item():.4f}")

    return total_loss / total if total > 0 else 0, correct / total if total > 0 else 0

def evaluate(model, dataloader, criterion, device):
    """Evaluate on a dataset."""
    model.eval()
    total_loss = 0
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in tqdm(dataloader, desc="Evaluating", leave=False):
            images, labels = images.to(device), labels.to(device)

            # Skip batches with invalid labels
            valid_mask = labels >= 0
            if valid_mask.sum() == 0:
                continue

            images = images[valid_mask]
            labels = labels[valid_mask]

            outputs = model(images)
            loss = criterion(outputs, labels)

            total_loss += loss.item() * labels.size(0)
            _, predicted = outputs.max(1)
            correct += predicted.eq(labels).sum().item()
            total += labels.size(0)

    return total_loss / total if total > 0 else 0, correct / total if total > 0 else 0

def main():
    CHECKPOINT_DIR.mkdir(exist_ok=True)

    # ========================================================================
    # Data
    # ========================================================================
    print("[*] Loading pantry dataset...")
    transform_train = transforms.Compose([
        transforms.RandomResizedCrop(IMG_SIZE),
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

    dataset = PantryDataset(DATA_DIR, transform_train)
    num_classes = len(dataset.classes)

    # Split into train/val/test
    train_size = int(len(dataset) * TRAIN_SPLIT)
    val_size = int(len(dataset) * VAL_SPLIT)
    test_size = len(dataset) - train_size - val_size

    train_dataset, val_dataset, test_dataset = random_split(
        dataset, [train_size, val_size, test_size]
    )

    # Apply different transforms to val/test
    val_dataset.dataset.transform = transform_val
    test_dataset.dataset.transform = transform_val

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=4)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=4)

    print(f"[OK] Train: {train_size}, Val: {val_size}, Test: {test_size}")

    # ========================================================================
    # Model
    # ========================================================================
    print("[*] Building model...")
    model = IngredientClassifierPantry(num_classes).to(DEVICE)
    optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE)
    criterion = nn.CrossEntropyLoss()
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=NUM_EPOCHS)

    best_val_acc = 0
    patience_counter = 0

    # ========================================================================
    # Training Loop
    # ========================================================================
    print("[*] Starting training...")
    for epoch in range(NUM_EPOCHS):
        print(f"\n[Epoch {epoch+1}/{NUM_EPOCHS}]")

        train_loss, train_acc = train_epoch(model, train_loader, optimizer, criterion, DEVICE)
        val_loss, val_acc = evaluate(model, val_loader, criterion, DEVICE)
        scheduler.step()

        print(f"  Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f}")
        print(f"  Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.4f}")

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
