# 🍳 SmartKitchen: A Vision-Language Cooking Assistant

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![Next.js](https://img.shields.io/badge/Next.js-Frontend-000000)
![CLIP](https://img.shields.io/badge/CLIP-Vision-412991)
![Qwen](https://img.shields.io/badge/Qwen2.5-LLM-FF6B35)
![OpenStreetMap](https://img.shields.io/badge/Geospatial-OpenStreetMap-green)
![License](https://img.shields.io/badge/License-Academic-lightgrey)

A modern, full-stack multimodal AI application that combines **CLIP zero-shot vision**, **joint embeddings**, **retrieval-augmented generation (RAG)**, and **location-aware recommendations** to help users identify dishes, detect ingredients, find recipes, and locate nearby restaurants or grocery stores.

> **MSc Deep Learning Coursework Project** — Now in production on Vercel + DigitalOcean

---

## 🚀 Live Demo

- **Frontend**: https://smartkitchen-three.vercel.app
- **Backend API**: https://smartktchen.duckdns.org

---

## ✨ Features

- 🍝 **Zero-Shot Dish Recognition**
  Identify prepared meals using **CLIP ViT-L/14** — works on 230+ food categories without retraining.

- 🧺 **Multi-Label Ingredient Detection**
  Detect up to **28 ingredients** simultaneously with zero-shot CLIP multi-label classification.

- 📖 **Hybrid Recipe Retrieval**
  - **Joint Embedding Search**: TF-IDF + SVD + Ridge regression for semantic recipe matching
  - **Fuzzy Matching Fallback**: SequenceMatcher for edge cases
  - Returns **2,000+ recipes** ranked by relevance, with cooking steps, nutrition, and substitution rules.

- 🤖 **Intelligent Query Assistant**
  - **RAG-powered**: Dynamically retrieves relevant recipes for each question
  - **Qwen2.5 LLM**: Text-only or multimodal (Llama 3.2-Vision) via Ollama
  - **Conversation Memory**: 5-turn history with structured formatting

- 📍 **Location Awareness**
  Find nearby **restaurants** or **grocery stores** using **OpenStreetMap** (Overpass API).

- 💾 **Persistent User State**
  - Recipe history tracking with timestamps (max 20, auto-deduped)
  - User preferences saved to localStorage
  - Detection context survives page navigation

- 🎯 **Modern Web Interface**
  Built with **Next.js 16 + Tailwind CSS v4** — responsive, fast, accessible.

## Architecture

```mermaid
graph TD
    A[User uploads image] --> B{Mode?}
    B -->|Dish| C[Dish Classifier<br>ResNet50 + Food-101]
    B -->|Ingredients| D[Ingredient Classifier<br>ResNet50 Multi-label]
    C --> E[Predicted Dish Label]
    D --> F[Detected Ingredient List]
    E --> G[Recipe Engine<br>Fuzzy match]
    F --> G
    G --> H[Recipe Suggestions<br>+ Missing Ingredients<br>+ Substitutions]
    H --> I[Query Assistant<br>FLAN-T5 RAG]
    I --> J[Grounded Answer]
    H --> K{Buy Instead?}
    K -->|Restaurants| L[Location Service<br>OpenStreetMap]
    K -->|Groceries| L
    L --> I
```

---

## Dataset Setup

Neither large dataset is included in this repository. Follow the instructions below before training.

---

### Food-101 (Dish Classifier)

**Auto-downloaded** — no manual steps needed.

When you run the dish training script, torchvision downloads Food-101 automatically into `data/food101/`:

```bash
python training/train_dish.py --data-dir data/food101
```

After downloading, the folder will look like this:

```
data/
└── food101/
    ├── food-101.tar.gz         # Downloaded archive (4.7 GB)
    └── food-101/
        ├── images/             # 101 class folders, ~1,000 images each (5 GB)
        ├── meta/
        │   ├── classes.txt
        │   ├── labels.txt
        │   ├── train.json
        │   ├── train.txt
        │   ├── test.json
        │   └── test.txt
        ├── README.txt
        └── license_agreement.txt
```

> Total size: ~10 GB (archive + extracted). `data/food101/` is listed in `.gitignore`.

---

### Food.com (Recipe Engine)

Must be downloaded manually from Kaggle:

**[Food.com Recipes and User Interactions](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions)**

Download and extract the archive, then place all files under `data/foodcom/`:

```
data/
└── foodcom/
    ├── PP_recipes.csv              # Pre-processed recipes (195 MB)
    ├── PP_users.csv                # Pre-processed user data (13 MB)
    ├── RAW_recipes.csv             # Raw recipe data (281 MB)
    ├── RAW_interactions.csv        # Raw user interactions (333 MB)
    ├── ingr_map.pkl                # Ingredient ID mapping (897 KB)
    ├── interactions_train.csv      # Train split (27 MB)
    ├── interactions_validation.csv # Validation split (285 KB)
    └── interactions_test.csv       # Test split (510 KB)
```

> `data/foodcom/` is listed in `.gitignore` and will never be committed to the repo.

---

## Quick Start

### 1. Install dependencies

```bash
cd smartkitchen
pip install -r requirements.txt
```

### 2. Run the Application

```bash
streamlit run app/streamlit_app.py
```

The app loads **trained ResNet50 models** for both dish and ingredient recognition. The system draws from a database of 2,000+ recipes and location-aware services for nearby recommendations.

### 3. Training & Evaluation (Optional)

If you wish to retrain the models:

**Dish classifier** (Food-101 ~5 GB):
```bash
python training/train_dish.py --epochs 10 --subset-size 10 --batch-size 32
```

**Ingredient classifier**:
```bash
python training/train_ingredients.py --epochs 15 --batch-size 32
```

**Run evaluation suite**:
```bash
python training/evaluate.py --component all
```

---

## Project Structure

```
smartkitchen/
│
├── app/
│   └── streamlit_app.py          # Streamlit interface
│
├── data/
│   ├── recipes.json              # 2,026 recipes with substitutions
│   ├── substitutions.json        # 54 ingredient substitution rules
│   ├── food101/                  # Food-101 dataset (auto-downloaded)
│   ├── grocery_dataset/          # Expanded ingredient dataset
│   └── pantry_images/            # Custom ingredient dataset
│
├── models/
│   ├── dish_classifier.py        # ResNet50 dish recognition
│   ├── ingredient_classifier.py  # ResNet50 multi-label ingredient detection
│   └── query_assistant.py        # FLAN-T5 RAG query assistant
│
├── training/
│   ├── train_dish.py             # Dish classifier training
│   ├── train_ingredients.py      # Ingredient classifier training
│   └── evaluate.py               # Full evaluation suite
│
├── utils/
│   ├── recipe_engine.py          # Recipe retrieval & ranking
│   ├── retrieval.py              # Context retrieval for RAG
│   ├── location_service.py       # Nearby restaurants/groceries (Overpass API)
│   └── prompt_builder.py         # Prompt template builder
│
├── outputs/
│   ├── saved_models/             # Trained model checkpoints (.pth)
│   ├── plots/                    # Evaluation metrics
│   └── predictions/              # Sample outputs
│
├── requirements.txt
└── README.md
```

---

## 📸 System Demo

| Dish Recognition | Ingredient Recognition |
|-----------------|-----------------------|
| Identify prepared meals | Detect pantry ingredients |
| Retrieve recipe | Suggest meals you can cook |
| Find nearby restaurants | Find nearby grocery stores |
 
---

## Functional Modes

### Mode 1 — Dish Recognition
1. Upload a photo of a prepared meal.
2. ResNet50 identifies the dish (top-3 predictions).
3. Recipe Engine retrieves the exact recipe and cooking steps.
4. Query Assistant answers follow-up questions (e.g., "Is this spicy?").
5. **Location Integration**: Find top-rated nearby restaurants serving that dish.

### Mode 2 — Ingredient Recognition
1. Upload a photo of pantry items.
2. ResNet50-ML detects multiple ingredients simultaneously.
3. Recipe Engine ranks 2,000+ recipes by ingredient overlap (`score = matched / total`).
4. Missing ingredients are flagged with 50+ substitution rules applied.
5. **Location Integration**: Find nearby grocery stores to buy missing items.

---

## AI Components

| Component | Model | Dataset | Loss/Task | Output |
|-----------|-------|---------|-----------|--------|
| Dish Classifier | ResNet50 | Food-101 (101-class) | CrossEntropy | Dish label + confidence |
| Ingredient Classifier | ResNet50-ML | Grocery Store Dataset | BCEWithLogits | 28 Multi-label classes |
| Query Assistant | FLAN-T5-small | RAG (Context-based) | Seq2Seq Gen | Grounded text answer |

---

## Datasets

### Food-101 Extension
- Trained on the full Food-101 taxonomy for comprehensive dish recognition.

### Expanded Ingredient Vocabulary
Recognition for **28** core ingredients:
`onion, tomato, garlic, milk, pepper, potato, apple, avocado, banana, kiwi, lemon, lime, mango, melon, orange, pear, pineapple, plum, pomegranate, asparagus, aubergine, cabbage, carrot, cucumber, ginger, leek, mushroom, zucchini`.

### 2,000+ Recipes
The `recipes.json` database is derived from Food.com, structured for fuzzy-matching and ingredient-overlap scoring.

---

## Query Assistant

Uses **retrieval-augmented generation (RAG)**:

1. `ContextRetriever` extracts metadata from the vision models and location services.
2. `PromptBuilder` constructs a grounded persona (Cooking Assistant).
3. FLAN-T5-small generates concise, factual answers based *only* on the detected context.

---

## 🧠 Tech Stack

- **Deep Learning:** PyTorch
- **Vision Models:** ResNet50
- **Language Models:** FLAN-T5 (Hugging Face Transformers)
- **Frontend:** Streamlit
- **Data Processing:** Pandas, NumPy
- **Evaluation:** Scikit-learn
- **Mapping:** OpenStreetMap (Overpass API)

---

## License

Academic project — MSc Deep Learning coursework.
