"""
Download Test Images for Dish Recognition
==========================================
Downloads one representative image per dish class from Wikimedia Commons.

Usage
-----
    cd smartkitchen
    python data/download_test_images.py

Output
------
    data/test_images/<class_name>/<class_name>.jpg
"""

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

# The 10 classes used by DishClassifier (DEFAULT_CLASSES)
DISH_CLASSES = [
    "apple_pie",
    "caesar_salad",
    "chocolate_cake",
    "fish_and_chips",
    "fried_rice",
    "grilled_salmon",
    "hamburger",
    "omelette",
    "pizza",
    "spaghetti_bolognese",
]

# Human-friendly search terms for the Wikimedia Commons API
SEARCH_QUERIES = {
    "apple_pie":         "apple pie food",
    "caesar_salad":      "Caesar salad food",
    "chocolate_cake":    "chocolate cake food",
    "fish_and_chips":    "fish and chips food",
    "fried_rice":        "fried rice food",
    "grilled_salmon":    "grilled salmon food",
    "hamburger":         "hamburger food",
    "omelette":          "omelette food",
    "pizza":             "pizza food",
    "spaghetti_bolognese": "spaghetti bolognese food",
}

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
OUT_DIR = Path(__file__).parent / "test_images"


def _api_get(params: dict) -> dict:
    """Send a GET request to the Wikimedia Commons API and return parsed JSON."""
    params["format"] = "json"
    url = COMMONS_API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "SmartKitchen-TestDownloader/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def find_image_url(query: str) -> str | None:
    """Return the URL of the first suitable JPEG/PNG from a Commons search."""
    search_params = {
        "action": "query",
        "generator": "search",
        "gsrnamespace": 6,          # File namespace
        "gsrsearch": query,
        "gsrlimit": 10,
        "prop": "imageinfo",
        "iiprop": "url|mime|size|thumburl",
        "iiurlwidth": 512,          # Request a 512 px thumbnail (avoids rate-limit on originals)
    }
    data = _api_get(search_params)
    pages = data.get("query", {}).get("pages", {})

    for page in pages.values():
        info = page.get("imageinfo", [{}])[0]
        mime = info.get("mime", "")
        width = info.get("width", 0)
        height = info.get("height", 0)
        thumb = info.get("thumburl", "")

        # Prefer JPEG/PNG images with a valid thumbnail URL
        if mime in ("image/jpeg", "image/png") and width >= 400 and height >= 300 and thumb:
            return thumb

    return None


def download(url: str, dest: Path) -> None:
    """Download a file from *url* and save it to *dest*."""
    req = urllib.request.Request(url, headers={"User-Agent": "SmartKitchen-TestDownloader/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp, open(dest, "wb") as f:
        f.write(resp.read())


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ok, failed = [], []

    for dish in DISH_CLASSES:
        query = SEARCH_QUERIES[dish]
        class_dir = OUT_DIR / dish
        class_dir.mkdir(exist_ok=True)

        # Skip if already downloaded
        existing = list(class_dir.glob(f"{dish}.*"))
        if existing:
            print(f"[{dish}] already exists, skipping.")
            ok.append(dish)
            continue

        print(f"[{dish}] Searching …", end=" ", flush=True)
        for attempt in range(3):
            try:
                img_url = find_image_url(query)
                if img_url is None:
                    print("no suitable image found.")
                    failed.append(dish)
                    break

                ext = "jpg" if "jpeg" in img_url.lower() or img_url.lower().endswith(".jpg") else "png"
                dest = class_dir / f"{dish}.{ext}"
                download(img_url, dest)
                size_kb = dest.stat().st_size // 1024
                print(f"saved ({size_kb} KB) → {dest.relative_to(Path(__file__).parent.parent)}")
                ok.append(dish)
                break
            except Exception as exc:
                if "429" in str(exc) and attempt < 2:
                    wait = 10 * (attempt + 1)
                    print(f"rate-limited, retrying in {wait}s …", end=" ", flush=True)
                    time.sleep(wait)
                else:
                    print(f"ERROR – {exc}")
                    failed.append(dish)
                    break

        time.sleep(2)   # be polite to the API

    print(f"\n✓ {len(ok)}/{len(DISH_CLASSES)} images downloaded to {OUT_DIR}")
    if failed:
        print(f"✗ Failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
