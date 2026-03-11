"""
Pantry Ingredient Dataset Preparation
======================================
Downloads sample ingredient images from the Open Images Dataset (OID)
or sets up the directory structure for a custom dataset, plus generates
a multi-label CSV annotation file.

This script supports two modes:

1. **Auto-download** (default): Downloads sample images from URLs or
   uses Open Images v7 to populate each ingredient folder.

2. **Setup-only**: Creates the directory structure and annotation
   template, ready for manual image collection.

Ingredient classes (11):
    egg, onion, tomato, garlic, rice, pasta, bread, milk, cheese, pepper, potato

Usage
-----
    # Set up directory structure + download from Open Images
    python data/prepare_pantry_dataset.py --mode download --images-per-class 150

    # Set up directory structure only (for manual collection)
    python data/prepare_pantry_dataset.py --mode setup

    # Generate multi-label CSV from populated ImageFolder
    python data/prepare_pantry_dataset.py --mode generate-csv
"""

import argparse
import csv
import os
import sys
import json
import random
from pathlib import Path
from typing import List

INGREDIENT_CLASSES = [
    "onion", "tomato", "garlic", "milk", "pepper", "potato",
    "apple", "avocado", "banana", "kiwi", "lemon", "lime", 
    "mango", "melon", "orange", "pear", "pineapple", "plum", 
    "pomegranate", "asparagus", "aubergine", "cabbage", "carrot", 
    "cucumber", "ginger", "leek", "mushroom", "zucchini"
]

# Mapping from our pantry classes to Grocery Store Dataset classes
GROCERY_DATASET_MAP = {
    "onion": ["Yellow-Onion"],
    "tomato": ["Regular-Tomato", "Beef-Tomato", "Vine-Tomato"],
    "garlic": ["Garlic"],
    "milk": [
        "Arla-Standard-Milk", "Arla-Lactose-Medium-Fat-Milk", 
        "Arla-Ecological-Medium-Fat-Milk", "Arla-Medium-Fat-Milk", 
        "Garant-Ecological-Medium-Fat-Milk", "Garant-Ecological-Standard-Milk"
    ],
    "pepper": ["Green-Bell-Pepper", "Red-Bell-Pepper", "Orange-Bell-Pepper", "Yellow-Bell-Pepper"],
    "potato": ["Solid-Potato", "Floury-Potato", "Sweet-Potato"],
    # Expanded Fruits
    "apple": ["Golden-Delicious", "Granny-Smith", "Pink-Lady", "Red-Delicious", "Royal-Gala"],
    "avocado": ["Avocado"],
    "banana": ["Banana"],
    "kiwi": ["Kiwi"],
    "lemon": ["Lemon"],
    "lime": ["Lime"],
    "mango": ["Mango"],
    "melon": ["Cantaloupe", "Galia-Melon", "Honeydew-Melon", "Watermelon"],
    "orange": ["Orange"],
    "pear": ["Anjou", "Conference", "Kaiser"],
    "pineapple": ["Pineapple"],
    "plum": ["Plum"],
    "pomegranate": ["Pomegranate"],
    # Expanded Vegetables
    "asparagus": ["Asparagus"],
    "aubergine": ["Aubergine"],
    "cabbage": ["Cabbage"],
    "carrot": ["Carrots"],
    "cucumber": ["Cucumber"],
    "ginger": ["Ginger"],
    "leek": ["Leek"],
    "mushroom": ["Brown-Cap-Mushroom"],
    "zucchini": ["Zucchini"],
}

def ingest_grocery_dataset(data_dir: str, grocery_root: str):
    """
    Ingest images from the Marcus Gawlowicz 'Grocery Store Dataset'.
    Parses the directory structure and copies matched images to pantry folders.
    """
    print(f"\nIngesting data from Grocery Store Dataset at: {grocery_root}")
    
    # Identify the base dataset directory (handling nested 'GroceryStoreDataset/dataset')
    base_dir = os.path.join(grocery_root, "dataset")
    if not os.path.exists(base_dir):
        base_dir = os.path.join(grocery_root, "GroceryStoreDataset/dataset")
    
    if not os.path.exists(base_dir):
        print(f"✗ Error: Dataset directory not found in {grocery_root}")
        return

    import shutil
    splits = ["train", "val", "test"]
    
    report = {ing: 0 for ing in INGREDIENT_CLASSES}
    matched_source_folders = set()

    for ingredient, target_folders in GROCERY_DATASET_MAP.items():
        dst_dir = os.path.join(data_dir, ingredient)
        os.makedirs(dst_dir, exist_ok=True)
        
        for split in splits:
            split_dir = os.path.join(base_dir, split)
            if not os.path.exists(split_dir): continue
            
            # Recursive check for target folders
            for root, dirs, files in os.walk(split_dir):
                for d in dirs:
                    if d in target_folders:
                        src_cls_dir = os.path.join(root, d)
                        matched_source_folders.add(d)
                        for img_name in os.listdir(src_cls_dir):
                            if img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                                src_path = os.path.join(src_cls_dir, img_name)
                                dst_name = f"{split}_{d}_{img_name}"
                                dst_path = os.path.join(dst_dir, dst_name)
                                if not os.path.exists(dst_path):
                                    shutil.copy2(src_path, dst_path)
                                    report[ingredient] += 1

    # Report
    print("\n" + "="*50)
    print("GROCERY DATASET INGESTION REPORT")
    print("="*50)
    print(f"Matched {len(matched_source_folders)} specific folders from source.")
    
    missing = [ing for ing in INGREDIENT_CLASSES if report[ing] == 0]
    
    print("\nImage counts per target:")
    for ing, count in report.items():
        status = "✓ Matched" if count > 0 else "✗ Missing"
        print(f"  - {ing:<10}: {count:>4} images ({status})")

    if missing:
        print("\n" + "!" * 50)
        print("MISSING CLASSES (Fallback required)")
        print("!" * 50)
        print(f"The following ingredients were not found in this dataset: {', '.join(missing)}")
        print("Please add ~100 images for each to their folders in data/pantry_images/")
        print("!" * 50 + "\n")


def generate_csv_annotations(data_dir: str, output_csv: str):
    """Generate a multi-label CSV from the ImageFolder structure.

    For ImageFolder (single-label), each image gets a 1 only for
    its folder's ingredient class.
    """
    rows = []
    for cls in INGREDIENT_CLASSES:
        cls_dir = os.path.join(data_dir, cls)
        if not os.path.isdir(cls_dir):
            continue
        for fname in os.listdir(cls_dir):
            if not fname.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                continue
            # Build multi-label row (1 for this class, 0 for others)
            label_row = {c: 0 for c in INGREDIENT_CLASSES}
            label_row[cls] = 1
            label_row["filename"] = os.path.join(cls, fname)
            rows.append(label_row)

    if not rows:
        print(f"No images found in {data_dir}/")
        print("Add images to the ingredient folders first.")
        return

    # Write CSV
    fieldnames = ["filename"] + INGREDIENT_CLASSES
    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        random.shuffle(rows)
        writer.writerows(rows)

    print(f"\n✓ Generated annotation CSV: {output_csv}")
    print(f"  Total images: {len(rows)}")
    for cls in INGREDIENT_CLASSES:
        count = sum(1 for r in rows if r[cls] == 1)
        print(f"  {cls}: {count} images")


def print_dataset_summary(data_dir: str):
    """Print current dataset status."""
    print(f"\n{'='*50}")
    print(f"Dataset Summary: {data_dir}")
    print(f"{'='*50}")
    total = 0
    for cls in INGREDIENT_CLASSES:
        cls_dir = os.path.join(data_dir, cls)
        if os.path.isdir(cls_dir):
            count = len([f for f in os.listdir(cls_dir)
                        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))])
        else:
            count = 0
        status = "✓" if count >= 100 else ("⚠" if count > 0 else "✗")
        total += count
        print(f"  {status} {cls}: {count} images")
    print(f"\n  Total: {total} images")
    if total >= 100 * len(INGREDIENT_CLASSES):
        print("  Status: Ready for training!")
    elif total > 0:
        print("  Status: Partially populated — add more images for better results")
    else:
        print("  Status: Empty — add images to ingredient folders")


def main():
    parser = argparse.ArgumentParser(description="Prepare Pantry Ingredient Dataset")
    parser.add_argument(
        "--mode",
        type=str,
        default="setup",
        choices=["setup", "download", "generate-csv", "summary"],
        help="Operation mode (use 'download' to ingest from Grocery Store Dataset)",
    )
    parser.add_argument("--data-dir", type=str, default="data/pantry_images")
    parser.add_argument("--grocery-dir", type=str, default="data/grocery_dataset", help="Path to Marcus Gawlowicz Grocery Store Dataset")
    parser.add_argument("--images-per-class", type=int, default=150)
    parser.add_argument("--csv-output", type=str, default="data/pantry_images/pantry_labels.csv")
    parser.add_argument("--clean", action="store_true", help="Delete existing images before downloading")
    args = parser.parse_args()

    if args.clean and args.mode in ["setup", "download"]:
        print(f"Cleaning existing data in {args.data_dir}...")
        for cls in INGREDIENT_CLASSES:
            cls_dir = os.path.join(args.data_dir, cls)
            if os.path.exists(cls_dir):
                import shutil
                shutil.rmtree(cls_dir)

    if args.mode == "setup":
        for cls in INGREDIENT_CLASSES:
            os.makedirs(os.path.join(args.data_dir, cls), exist_ok=True)
        print_dataset_summary(args.data_dir)

    elif args.mode == "download":
        # Ensure directories exist
        for cls in INGREDIENT_CLASSES:
            os.makedirs(os.path.join(args.data_dir, cls), exist_ok=True)
        
        # Ingest from the high-quality Grocery Store Dataset
        ingest_grocery_dataset(args.data_dir, args.grocery_dir)
        
        # Finally generate labels
        generate_csv_annotations(args.data_dir, args.csv_output)
        print_dataset_summary(args.data_dir)

    elif args.mode == "generate-csv":
        generate_csv_annotations(args.data_dir, args.csv_output)

    elif args.mode == "summary":
        print_dataset_summary(args.data_dir)


if __name__ == "__main__":
    main()
