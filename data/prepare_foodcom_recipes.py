"""
Food.com Recipe Dataset Processor
===================================
Downloads and processes the Food.com Recipes dataset from Kaggle into
the SmartKitchen ``recipes.json`` format.

Prerequisites
-------------
1. Install the Kaggle CLI: ``pip install kaggle``
2. Set up Kaggle API credentials:
   - Go to https://www.kaggle.com/settings → "Create New Token"
   - Save ``kaggle.json`` to ``~/.kaggle/kaggle.json``
   - Run ``chmod 600 ~/.kaggle/kaggle.json``

Usage
-----
    # Download from Kaggle and process
    python data/prepare_foodcom_recipes.py --download --subset-size 1000

    # Process an already-downloaded CSV
    python data/prepare_foodcom_recipes.py --csv-path data/foodcom/RAW_recipes.csv --subset-size 1000
"""

import argparse
import ast
import json
import os
import random
import sys
from pathlib import Path

# Common ingredient names used for substitution matching
KNOWN_INGREDIENTS = {
    "egg", "eggs", "onion", "onions", "tomato", "tomatoes", "garlic",
    "rice", "pasta", "bread", "milk", "cheese", "pepper", "peppers",
    "potato", "potatoes", "butter", "flour", "sugar", "salt",
    "olive oil", "vegetable oil", "chicken", "beef", "pork", "fish",
    "cream", "sour cream", "yogurt", "lemon", "lime", "ginger",
    "mushroom", "mushrooms", "carrot", "carrots", "celery", "corn",
    "spinach", "broccoli", "cucumber", "lettuce", "basil", "parsley",
    "cilantro", "thyme", "oregano", "cumin", "paprika", "cinnamon",
    "soy sauce", "vinegar", "honey", "maple syrup",
}

# Substitution rules to attach to processed recipes
DEFAULT_SUBSTITUTIONS = {
    "egg": ["tofu scramble", "flax egg"],
    "milk": ["oat milk", "almond milk"],
    "butter": ["olive oil", "coconut oil"],
    "cream": ["coconut cream", "cashew cream"],
    "cheese": ["nutritional yeast", "vegan cheese"],
    "pasta": ["rice noodles", "gluten-free pasta"],
    "rice": ["quinoa", "cauliflower rice"],
    "bread": ["gluten-free bread", "tortilla wrap"],
    "onion": ["shallot", "leek"],
    "garlic": ["garlic powder", "shallot"],
    "tomato": ["passata", "sun-dried tomatoes"],
    "pepper": ["courgette", "mushroom"],
    "potato": ["sweet potato", "cauliflower"],
}


def download_kaggle_dataset(output_dir: str):
    """Download the Food.com dataset using the Kaggle CLI."""
    os.makedirs(output_dir, exist_ok=True)
    print("Downloading Food.com dataset from Kaggle...")
    exit_code = os.system(
        f"kaggle datasets download -d shuyangli94/food-com-recipes-and-user-interactions "
        f"-p {output_dir} --unzip"
    )
    if exit_code != 0:
        print("\nERROR: Kaggle download failed.")
        print("Make sure you have:")
        print("  1. pip install kaggle")
        print("  2. Kaggle API token at ~/.kaggle/kaggle.json")
        print("  3. Accepted dataset terms at:")
        print("     https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions")
        sys.exit(1)
    print(f"Dataset downloaded to: {output_dir}")


def parse_steps(steps_str: str) -> list:
    """Parse steps from Food.com format (Python list stored as string)."""
    try:
        steps = ast.literal_eval(steps_str)
        if isinstance(steps, list):
            return [s.strip() for s in steps if s.strip()]
    except (ValueError, SyntaxError):
        pass
    return [steps_str.strip()] if isinstance(steps_str, str) and steps_str.strip() else []


def parse_ingredients(ingredients_str: str) -> list:
    """Parse ingredients from Food.com format."""
    try:
        ingredients = ast.literal_eval(ingredients_str)
        if isinstance(ingredients, list):
            return [i.strip().lower() for i in ingredients if i.strip()]
    except (ValueError, SyntaxError):
        pass
    return []


def parse_tags(tags_str: str) -> list:
    """Parse tags from Food.com format."""
    try:
        tags = ast.literal_eval(tags_str)
        if isinstance(tags, list):
            return [t.strip().lower() for t in tags if t.strip()]
    except (ValueError, SyntaxError):
        pass
    return []


def infer_cuisine(tags: list, name: str) -> str:
    """Infer cuisine from tags and recipe name."""
    cuisine_map = {
        "italian": ["italian", "pasta", "pizza", "risotto", "lasagna"],
        "mexican": ["mexican", "taco", "burrito", "enchilada", "salsa"],
        "chinese": ["chinese", "stir-fry", "wok", "dim sum", "fried rice"],
        "indian": ["indian", "curry", "tandoori", "naan", "masala"],
        "japanese": ["japanese", "sushi", "ramen", "teriyaki", "miso"],
        "french": ["french", "croissant", "soufflé", "crêpe", "baguette"],
        "thai": ["thai", "pad thai", "coconut curry"],
        "american": ["american", "bbq", "burger", "mac and cheese"],
        "mediterranean": ["mediterranean", "greek", "hummus", "falafel"],
        "british": ["british", "english", "scone", "fish and chips"],
    }
    all_text = " ".join(tags) + " " + name.lower()
    for cuisine, keywords in cuisine_map.items():
        if any(kw in all_text for kw in keywords):
            return cuisine.title()
    return "International"


def infer_category(tags: list, name: str) -> str:
    """Infer category from tags and recipe name."""
    all_text = " ".join(tags) + " " + name.lower()
    if any(kw in all_text for kw in ["breakfast", "brunch", "pancake", "waffle", "omelette"]):
        return "breakfast"
    if any(kw in all_text for kw in ["dessert", "cake", "cookie", "pie", "sweet", "chocolate"]):
        return "dessert"
    if any(kw in all_text for kw in ["soup", "stew", "chowder", "broth"]):
        return "soup"
    if any(kw in all_text for kw in ["salad", "side dish", "side"]):
        return "side"
    if any(kw in all_text for kw in ["appetizer", "starter", "snack"]):
        return "starter"
    if any(kw in all_text for kw in ["drink", "beverage", "smoothie", "cocktail"]):
        return "drink"
    return "main"


def build_substitutions(ingredients: list) -> dict:
    """Build substitution dict for ingredients that match known rules."""
    subs = {}
    for ing in ingredients:
        for key, alts in DEFAULT_SUBSTITUTIONS.items():
            if key in ing.lower():
                subs[ing] = alts
                break
    return subs


def process_foodcom_csv(csv_path: str, subset_size: int = 1000) -> list:
    """Process the Food.com RAW_recipes.csv into SmartKitchen format."""
    import pandas as pd

    print(f"Loading {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} recipes from Food.com")

    # Filter: must have name, ingredients, steps, and reasonable prep time
    df = df.dropna(subset=["name", "ingredients", "steps", "minutes"])
    df = df[df["minutes"] > 0]
    df = df[df["minutes"] <= 180]  # Max 3 hours

    # Parse ingredients and filter recipes with 3-15 ingredients
    df["parsed_ingredients"] = df["ingredients"].apply(parse_ingredients)
    df["n_ingredients"] = df["parsed_ingredients"].apply(len)
    df = df[(df["n_ingredients"] >= 3) & (df["n_ingredients"] <= 15)]

    # Sort by number of interactions (n_steps as proxy for quality)
    df["parsed_steps"] = df["steps"].apply(parse_steps)
    df["n_steps"] = df["parsed_steps"].apply(len)
    df = df[df["n_steps"] >= 2]  # At least 2 steps

    # Parse tags
    if "tags" in df.columns:
        df["parsed_tags"] = df["tags"].apply(parse_tags)
    else:
        df["parsed_tags"] = [[] for _ in range(len(df))]

    # Sample subset
    if len(df) > subset_size:
        df = df.sample(n=subset_size, random_state=42)

    print(f"Processing {len(df)} recipes...")

    recipes = []
    for _, row in df.iterrows():
        name = str(row["name"]).strip().title()
        ingredients = row["parsed_ingredients"]
        steps = row["parsed_steps"]
        minutes = int(row["minutes"])
        tags = row["parsed_tags"]

        # Format prep time
        if minutes >= 60:
            hours = minutes // 60
            mins = minutes % 60
            prep_time = f"{hours} hour{'s' if hours > 1 else ''}"
            if mins > 0:
                prep_time += f" {mins} minutes"
        else:
            prep_time = f"{minutes} minutes"

        recipe = {
            "name": name,
            "ingredients": ingredients,
            "steps": steps,
            "prep_time": prep_time,
            "category": infer_category(tags, name),
            "cuisine": infer_cuisine(tags, name),
            "substitutions": build_substitutions(ingredients),
        }
        recipes.append(recipe)

    return recipes


def main():
    parser = argparse.ArgumentParser(description="Process Food.com recipes for SmartKitchen")
    parser.add_argument("--download", action="store_true", help="Download dataset from Kaggle first")
    parser.add_argument("--kaggle-dir", type=str, default="data/foodcom", help="Kaggle download directory")
    parser.add_argument("--csv-path", type=str, default=None, help="Path to RAW_recipes.csv")
    parser.add_argument("--subset-size", type=int, default=1000, help="Number of recipes to keep")
    parser.add_argument("--output", type=str, default="data/recipes.json", help="Output JSON path")
    parser.add_argument("--merge-existing", action="store_true", help="Merge with existing recipes.json")
    args = parser.parse_args()

    # Download if requested
    if args.download:
        download_kaggle_dataset(args.kaggle_dir)

    # Find CSV
    csv_path = args.csv_path
    if csv_path is None:
        csv_path = os.path.join(args.kaggle_dir, "RAW_recipes.csv")

    if not os.path.exists(csv_path):
        print(f"ERROR: CSV not found at {csv_path}")
        print("\nTo download the dataset, run:")
        print(f"  python {__file__} --download")
        print("\nOr download manually from:")
        print("  https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions")
        print(f"  Then place RAW_recipes.csv in {args.kaggle_dir}/")
        sys.exit(1)

    # Process
    recipes = process_foodcom_csv(csv_path, subset_size=args.subset_size)

    # Optionally merge with existing hand-curated recipes
    if args.merge_existing and os.path.exists(args.output):
        with open(args.output, "r") as f:
            existing = json.load(f)
        existing_names = {r["name"].lower() for r in existing}
        new_recipes = [r for r in recipes if r["name"].lower() not in existing_names]
        recipes = existing + new_recipes
        print(f"Merged: {len(existing)} existing + {len(new_recipes)} new = {len(recipes)} total")

    # Save
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(recipes, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(recipes)} recipes to {args.output}")

    # Print sample
    print("\nSample recipes:")
    for r in random.sample(recipes, min(3, len(recipes))):
        print(f"  {r['name']} ({r['cuisine']}) — {r['prep_time']} — {len(r['ingredients'])} ingredients")


if __name__ == "__main__":
    main()
