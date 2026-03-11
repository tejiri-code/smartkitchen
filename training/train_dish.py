"""
Dish Classifier Training Script
================================
Downloads Food-101 via torchvision, optionally filters to a subset of
classes, and trains a ResNet50-based classifier using transfer learning.

Usage
-----
    python training/train_dish.py --epochs 10 --subset-size 10 --batch-size 32
"""

import argparse
import os
import sys
import time

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets
import matplotlib.pyplot as plt

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.dish_classifier import DishClassifier, DEFAULT_CLASSES


def get_food101_subset(root: str, split: str, class_names: list, transform):
    """Load Food-101 and filter to selected classes only."""
    dataset = datasets.Food101(
        root=root, split=split, transform=transform, download=True
    )

    # Map selected class names to Food-101 internal indices
    all_classes = dataset.classes  # sorted list from torchvision
    selected_indices = []
    class_map = {}  # old_idx -> new_idx

    for new_idx, name in enumerate(class_names):
        if name in all_classes:
            old_idx = all_classes.index(name)
            class_map[old_idx] = new_idx
        else:
            print(f"  WARNING: Class '{name}' not found in Food-101, skipping.")

    # Filter samples
    filtered_indices = []
    for i in range(len(dataset)):
        _, label = dataset[i] if False else (None, dataset._labels[i])
        if label in class_map:
            filtered_indices.append(i)

    # Create a subset with re-mapped labels
    subset = Subset(dataset, filtered_indices)
    subset.class_map = class_map
    subset.class_names = class_names
    return subset, class_map


class MappedSubset(torch.utils.data.Dataset):
    """Wraps a Subset and remaps labels to contiguous indices."""

    def __init__(self, dataset, indices, class_map, transform=None):
        self.dataset = dataset
        self.indices = indices
        self.class_map = class_map
        self.transform = transform

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, idx):
        real_idx = self.indices[idx]
        image, label = self.dataset[real_idx]
        new_label = self.class_map.get(label, label)
        return image, new_label


def build_dataloaders(args, device):
    """Build train and test dataloaders from Food-101."""
    model_tmp = DishClassifier(num_classes=args.subset_size, pretrained_backbone=False)
    train_transform = model_tmp.get_transforms(train=True)
    val_transform = model_tmp.get_transforms(train=False)

    class_names = DEFAULT_CLASSES[: args.subset_size]
    print(f"Using {len(class_names)} classes: {class_names}")

    # Download and load datasets
    print("Downloading/loading Food-101 dataset...")
    train_ds = datasets.Food101(
        root=args.data_dir, split="train", transform=train_transform, download=True
    )
    test_ds = datasets.Food101(
        root=args.data_dir, split="test", transform=val_transform, download=True
    )

    all_classes = train_ds.classes

    # Build class index mapping
    class_map = {}
    for new_idx, name in enumerate(class_names):
        if name in all_classes:
            old_idx = all_classes.index(name)
            class_map[old_idx] = new_idx

    # Filter indices
    train_indices = [
        i for i, label in enumerate(train_ds._labels) if label in class_map
    ]
    test_indices = [
        i for i, label in enumerate(test_ds._labels) if label in class_map
    ]

    print(f"Training samples: {len(train_indices)}, Test samples: {len(test_indices)}")

    train_mapped = MappedSubset(train_ds, train_indices, class_map)
    test_mapped = MappedSubset(test_ds, test_indices, class_map)

    train_loader = DataLoader(
        train_mapped,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        pin_memory=(device.type == "cuda"),
    )
    test_loader = DataLoader(
        test_mapped,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=(device.type == "cuda"),
    )

    return train_loader, test_loader, class_names


def train_one_epoch(model, loader, criterion, optimizer, device):
    """Train for one epoch, return average loss and accuracy."""
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0

    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += labels.size(0)

    return total_loss / total, correct / total


@torch.no_grad()
def evaluate(model, loader, criterion, device):
    """Evaluate on validation/test set, return loss and accuracy."""
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0

    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        loss = criterion(outputs, labels)

        total_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += labels.size(0)

    return total_loss / total, correct / total


def plot_training_curves(history, save_path):
    """Save training/validation loss and accuracy plots."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    epochs = range(1, len(history["train_loss"]) + 1)

    ax1.plot(epochs, history["train_loss"], "b-", label="Train Loss")
    ax1.plot(epochs, history["val_loss"], "r-", label="Val Loss")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Loss")
    ax1.set_title("Training & Validation Loss")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.plot(epochs, history["train_acc"], "b-", label="Train Accuracy")
    ax2.plot(epochs, history["val_acc"], "r-", label="Val Accuracy")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Accuracy")
    ax2.set_title("Training & Validation Accuracy")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Training curves saved to: {save_path}")


def main():
    parser = argparse.ArgumentParser(description="Train Food-101 Dish Classifier")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate")
    parser.add_argument("--subset-size", type=int, default=10, help="Number of Food-101 classes to use")
    parser.add_argument("--data-dir", type=str, default="data/food101", help="Data download directory")
    parser.add_argument("--save-dir", type=str, default="outputs/saved_models", help="Model save directory")
    parser.add_argument("--plot-dir", type=str, default="outputs/plots", help="Plot save directory")
    parser.add_argument("--num-workers", type=int, default=2, help="DataLoader workers")
    parser.add_argument("--freeze-epochs", type=int, default=3, help="Epochs to train with frozen backbone")
    args = parser.parse_args()

    # Create output directories
    os.makedirs(args.save_dir, exist_ok=True)
    os.makedirs(args.plot_dir, exist_ok=True)

    # Device
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"Using device: {device}")

    # Build dataloaders
    train_loader, test_loader, class_names = build_dataloaders(args, device)

    # Build model
    model = DishClassifier(
        num_classes=len(class_names),
        class_names=class_names,
        pretrained_backbone=True,
    ).to(device)

    # Phase 1: Train with frozen backbone
    print(f"\n{'='*60}")
    print(f"Phase 1: Frozen backbone training ({args.freeze_epochs} epochs)")
    print(f"{'='*60}")
    model.freeze_backbone()

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=args.lr,
    )

    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    best_val_acc = 0.0

    total_epochs = args.freeze_epochs + args.epochs

    for epoch in range(1, args.freeze_epochs + 1):
        t0 = time.time()
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = evaluate(model, test_loader, criterion, device)
        elapsed = time.time() - t0

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(train_acc)
        history["val_acc"].append(val_acc)

        print(
            f"Epoch [{epoch}/{total_epochs}] "
            f"Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f} | "
            f"Time: {elapsed:.1f}s"
        )

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), os.path.join(args.save_dir, "dish_classifier_best.pth"))

    # Phase 2: Fine-tune full model
    print(f"\n{'='*60}")
    print(f"Phase 2: Full fine-tuning ({args.epochs} epochs)")
    print(f"{'='*60}")
    model.unfreeze_backbone()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr * 0.1)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

    for epoch in range(args.freeze_epochs + 1, total_epochs + 1):
        t0 = time.time()
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = evaluate(model, test_loader, criterion, device)
        scheduler.step()
        elapsed = time.time() - t0

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(train_acc)
        history["val_acc"].append(val_acc)

        print(
            f"Epoch [{epoch}/{total_epochs}] "
            f"Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f} | "
            f"Time: {elapsed:.1f}s"
        )

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), os.path.join(args.save_dir, "dish_classifier_best.pth"))

    # Save final model
    torch.save(model.state_dict(), os.path.join(args.save_dir, "dish_classifier_final.pth"))
    print(f"\nBest validation accuracy: {best_val_acc:.4f}")

    # Plot training curves
    plot_training_curves(history, os.path.join(args.plot_dir, "dish_training_curves.png"))

    print("\nTraining complete!")


if __name__ == "__main__":
    main()
