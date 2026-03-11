"""
Ingredient Classifier Training Script
======================================
Trains a multi-label ResNet50 classifier for pantry ingredient
recognition.  Expects an ImageFolder-style dataset organised as:

    data/pantry_images/
        egg/
            img_001.jpg
            img_002.jpg
        onion/
            ...
        ...

Each folder name corresponds to an ingredient class.  Images may contain
multiple ingredients; the multi-label ground truth is derived from
folder assignment (single-label per image) or from an optional CSV
annotation file for true multi-label setups.

Usage
-----
    python training/train_ingredients.py --epochs 15 --batch-size 32

Dataset preparation guide
-------------------------
1.  Create a folder ``data/pantry_images/`` with one sub-folder per
    ingredient class (see INGREDIENT_CLASSES in the model file).
2.  Collect 100–300 images per class.  Good sources include:
    - Photographing your own pantry items
    - Filtered downloads from Open Images Dataset
    - Web scraping with appropriate licensing
3.  For multi-label images (e.g. an image showing both eggs and onions),
    create a ``data/pantry_labels.csv`` with filename and ingredient Boolean columns.
    Each cell is 0 or 1.
"""

import argparse
import os
import sys
import time
import csv

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision import datasets, transforms
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.ingredient_classifier import IngredientClassifier, INGREDIENT_CLASSES


# ------------------------------------------------------------------
# Dataset helpers
# ------------------------------------------------------------------
class MultiLabelIngredientDataset(Dataset):
    """Multi-label dataset loaded from a CSV annotation file.

    CSV format::

        filename,egg,onion,tomato,garlic,rice,pasta,bread,milk,cheese,pepper,potato
        img_001.jpg,1,0,1,0,0,0,0,0,0,0,0
        ...
    """

    def __init__(self, image_dir: str, csv_path: str, active_classes: list, transform=None):
        self.image_dir = image_dir
        self.transform = transform
        self.samples = []
        self.active_classes = active_classes
        self.num_classes = len(active_classes)

        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                fname = row["filename"]
                labels = [int(row.get(cls, 0)) for cls in active_classes]
                self.samples.append((fname, labels))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        fname, labels = self.samples[idx]
        img_path = os.path.join(self.image_dir, fname)
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        labels_tensor = torch.tensor(labels, dtype=torch.float32)
        return image, labels_tensor


class SingleLabelToMultiLabel(Dataset):
    """Wraps an ImageFolder dataset and converts single-label to
    multi-label (one-hot) targets — useful when each image has one
    primary ingredient only."""

    def __init__(self, image_folder_dataset, num_classes: int, class_names: list):
        self.dataset = image_folder_dataset
        self.num_classes = num_classes
        # Map ImageFolder class indices to our INGREDIENT_CLASSES order
        self.class_map = {}
        for folder_idx, folder_name in enumerate(image_folder_dataset.classes):
            if folder_name.lower() in [c.lower() for c in class_names]:
                target_idx = [c.lower() for c in class_names].index(folder_name.lower())
                self.class_map[folder_idx] = target_idx

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        image, folder_label = self.dataset[idx]
        multi_label = torch.zeros(self.num_classes, dtype=torch.float32)
        if folder_label in self.class_map:
            multi_label[self.class_map[folder_label]] = 1.0
        return image, multi_label


def build_dataloaders(args, device):
    """Build train/val dataloaders from either CSV or ImageFolder dataset."""
    csv_path = os.path.join(args.data_dir, "pantry_labels.csv")

    # Determine active classes (those present in CSV with images)
    active_classes = []
    if os.path.exists(csv_path):
        with open(csv_path, "r") as f:
            header = next(csv.reader(f))
            # Filename is first, then classes
            # Potentially only include those with at least one image?
            # For now, take all column names that match INGREDIENT_CLASSES
            potential_classes = header[1:]
            
            # Count images per class
            counts = {c: 0 for c in potential_classes}
            reader = csv.DictReader(f)
            # Reset file pointer if needed? No, just re-open or read all
        
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                for c in potential_classes:
                    if int(row.get(c, 0)) == 1:
                        counts[c] += 1
            
        active_classes = [c for c in potential_classes if counts[c] > 0]
        print(f"\nFinal Ingredient Vocabulary ({len(active_classes)} classes):")
        for c in active_classes:
            print(f"  - {c}: {counts[c]} images")
    else:
        # Fallback to folders
        active_classes = [d for d in os.listdir(args.data_dir) 
                         if os.path.isdir(os.path.join(args.data_dir, d)) and d in INGREDIENT_CLASSES]
        active_classes.sort()
        print(f"Using ImageFolder classes: {active_classes}")

    if not active_classes:
        print("ERROR: No active classes found in dataset.")
        sys.exit(1)

    model_tmp = IngredientClassifier(num_classes=len(active_classes), class_names=active_classes, pretrained_backbone=False)
    train_transform = model_tmp.get_transforms(train=True)
    val_transform = model_tmp.get_transforms(train=False)

    if os.path.exists(csv_path):
        print("Found pantry_labels.csv — loading multi-label dataset")
        full_dataset = MultiLabelIngredientDataset(
            args.data_dir, csv_path, active_classes, transform=train_transform
        )
    else:
        print("Loading ImageFolder dataset (single-label → multi-label)")
        raw_dataset = datasets.ImageFolder(args.data_dir, transform=train_transform)
        full_dataset = SingleLabelToMultiLabel(
            raw_dataset, len(active_classes), active_classes
        )

    # Split into train and validation
    n_total = len(full_dataset)
    n_val = max(1, int(0.2 * n_total))
    n_train = n_total - n_val
    train_ds, val_ds = random_split(full_dataset, [n_train, n_val])

    print(f"Training samples: {n_train}, Validation samples: {n_val}")

    train_loader = DataLoader(
        train_ds, batch_size=args.batch_size, shuffle=True,
        num_workers=args.num_workers, pin_memory=(device.type == "cuda"),
    )
    val_loader = DataLoader(
        val_ds, batch_size=args.batch_size, shuffle=False,
        num_workers=args.num_workers, pin_memory=(device.type == "cuda"),
    )

    # Calculate class weights for imbalance
    pos_weight = None
    if os.path.exists(csv_path):
        labels_list = []
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                labels_list.append([int(row.get(cls, 0)) for cls in active_classes])
        
        labels_arr = np.array(labels_list)
        pos_counts = labels_arr.sum(axis=0)
        neg_counts = len(labels_arr) - pos_counts
        weights = neg_counts / (pos_counts + 1e-8)
        pos_weight = torch.tensor(weights, dtype=torch.float32).to(device)
        print(f"Calculated pos_weight for imbalance: {weights.round(2)}")

    return train_loader, val_loader, pos_weight, active_classes


# ------------------------------------------------------------------
# Metrics
# ------------------------------------------------------------------
def compute_multilabel_metrics(preds: torch.Tensor, targets: torch.Tensor, threshold: float = 0.5):
    """Compute multi-label precision, recall, F1, and Hamming loss."""
    pred_binary = (preds >= threshold).float()

    tp = (pred_binary * targets).sum(dim=0)
    fp = (pred_binary * (1 - targets)).sum(dim=0)
    fn = ((1 - pred_binary) * targets).sum(dim=0)

    precision = tp / (tp + fp + 1e-8)
    recall = tp / (tp + fn + 1e-8)
    f1 = 2 * precision * recall / (precision + recall + 1e-8)

    hamming = (pred_binary != targets).float().mean().item()

    return {
        "precision": precision.mean().item(),
        "recall": recall.mean().item(),
        "f1": f1.mean().item(),
        "hamming_loss": hamming,
    }


# ------------------------------------------------------------------
# Training / evaluation loops
# ------------------------------------------------------------------
def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss = 0.0
    all_preds = []
    all_targets = []

    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * images.size(0)
        all_preds.append(torch.sigmoid(outputs).cpu())
        all_targets.append(labels.cpu())

    all_preds = torch.cat(all_preds)
    all_targets = torch.cat(all_targets)
    metrics = compute_multilabel_metrics(all_preds, all_targets)
    metrics["loss"] = total_loss / len(all_preds)
    return metrics


@torch.no_grad()
def evaluate_model(model, loader, criterion, device):
    model.eval()
    total_loss = 0.0
    all_preds = []
    all_targets = []

    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        loss = criterion(outputs, labels)

        total_loss += loss.item() * images.size(0)
        all_preds.append(torch.sigmoid(outputs).cpu())
        all_targets.append(labels.cpu())

    all_preds = torch.cat(all_preds)
    all_targets = torch.cat(all_targets)
    metrics = compute_multilabel_metrics(all_preds, all_targets)
    metrics["loss"] = total_loss / len(all_preds)
    return metrics


def plot_training_curves(history, save_path):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    epochs = range(1, len(history["train_loss"]) + 1)

    axes[0, 0].plot(epochs, history["train_loss"], "b-", label="Train")
    axes[0, 0].plot(epochs, history["val_loss"], "r-", label="Val")
    axes[0, 0].set_title("Loss (BCE)")
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].plot(epochs, history["train_f1"], "b-", label="Train")
    axes[0, 1].plot(epochs, history["val_f1"], "r-", label="Val")
    axes[0, 1].set_title("F1 Score")
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].plot(epochs, history["train_precision"], "b-", label="Train Precision")
    axes[1, 0].plot(epochs, history["val_precision"], "r-", label="Val Precision")
    axes[1, 0].plot(epochs, history["train_recall"], "b--", label="Train Recall")
    axes[1, 0].plot(epochs, history["val_recall"], "r--", label="Val Recall")
    axes[1, 0].set_title("Precision & Recall")
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].plot(epochs, history["val_hamming"], "r-", label="Val Hamming Loss")
    axes[1, 1].set_title("Hamming Loss")
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Training curves saved to: {save_path}")


def main():
    parser = argparse.ArgumentParser(description="Train Ingredient Classifier")
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--data-dir", type=str, default="data/pantry_images")
    parser.add_argument("--save-dir", type=str, default="outputs/saved_models")
    parser.add_argument("--plot-dir", type=str, default="outputs/plots")
    parser.add_argument("--num-workers", type=int, default=2)
    parser.add_argument("--freeze-epochs", type=int, default=5)
    args = parser.parse_args()

    os.makedirs(args.save_dir, exist_ok=True)
    os.makedirs(args.plot_dir, exist_ok=True)

    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    print(f"Using device: {device}")

    train_loader, val_loader, pos_weight, active_classes = build_dataloaders(args, device)

    model = IngredientClassifier(
        num_classes=len(active_classes),
        class_names=active_classes,
        pretrained_backbone=True,
    ).to(device)

    criterion = model.get_loss_fn(pos_weight=pos_weight)
    best_val_f1 = 0.0

    history = {
        "train_loss": [], "val_loss": [],
        "train_f1": [], "val_f1": [],
        "train_precision": [], "val_precision": [],
        "train_recall": [], "val_recall": [],
        "val_hamming": [],
    }

    total_epochs = args.freeze_epochs + args.epochs

    # Phase 1: Frozen backbone
    print(f"\n{'='*60}")
    print(f"Phase 1: Frozen backbone ({args.freeze_epochs} epochs)")
    print(f"{'='*60}")
    model.freeze_backbone()
    optimizer = torch.optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()), lr=args.lr
    )

    for epoch in range(1, args.freeze_epochs + 1):
        t0 = time.time()
        train_m = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_m = evaluate_model(model, val_loader, criterion, device)
        elapsed = time.time() - t0

        for key in ["loss", "f1", "precision", "recall"]:
            history[f"train_{key}"].append(train_m[key])
            history[f"val_{key}"].append(val_m[key])
        history["val_hamming"].append(val_m["hamming_loss"])

        print(
            f"Epoch [{epoch}/{total_epochs}] "
            f"Loss: {train_m['loss']:.4f}/{val_m['loss']:.4f} "
            f"F1: {train_m['f1']:.4f}/{val_m['f1']:.4f} "
            f"Hamming: {val_m['hamming_loss']:.4f} "
            f"({elapsed:.1f}s)"
        )

        if val_m["f1"] > best_val_f1:
            best_val_f1 = val_m["f1"]
            torch.save(model.state_dict(), os.path.join(args.save_dir, "ingredient_classifier_best.pth"))

    # Phase 2: Fine-tune
    print(f"\n{'='*60}")
    print(f"Phase 2: Full fine-tuning ({args.epochs} epochs)")
    print(f"{'='*60}")
    model.unfreeze_backbone()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr * 0.1)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

    for epoch in range(args.freeze_epochs + 1, total_epochs + 1):
        t0 = time.time()
        train_m = train_one_epoch(model, train_loader, criterion, optimizer, device)
        val_m = evaluate_model(model, val_loader, criterion, device)
        scheduler.step()
        elapsed = time.time() - t0

        for key in ["loss", "f1", "precision", "recall"]:
            history[f"train_{key}"].append(train_m[key])
            history[f"val_{key}"].append(val_m[key])
        history["val_hamming"].append(val_m["hamming_loss"])

        print(
            f"Epoch [{epoch}/{total_epochs}] "
            f"Loss: {train_m['loss']:.4f}/{val_m['loss']:.4f} "
            f"F1: {train_m['f1']:.4f}/{val_m['f1']:.4f} "
            f"Hamming: {val_m['hamming_loss']:.4f} "
            f"({elapsed:.1f}s)"
        )

        if val_m["f1"] > best_val_f1:
            best_val_f1 = val_m["f1"]
            torch.save(model.state_dict(), os.path.join(args.save_dir, "ingredient_classifier_best.pth"))

    torch.save(model.state_dict(), os.path.join(args.save_dir, "ingredient_classifier_final.pth"))
    print(f"\nBest validation F1: {best_val_f1:.4f}")

    plot_training_curves(history, os.path.join(args.plot_dir, "ingredient_training_curves.png"))
    print("\nTraining complete!")


if __name__ == "__main__":
    main()
