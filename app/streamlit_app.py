"""
SmartKitchen — Streamlit Demo Application
==========================================
An interactive web interface that brings together all SmartKitchen
components: dish recognition, ingredient detection, recipe suggestion,
the grounded Query Assistant, and nearby-place recommendations.

Launch
------
    cd smartkitchen
    streamlit run app/streamlit_app.py
"""

import os
import sys
import json
import requests

import streamlit as st
from PIL import Image

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.dish_classifier import DishClassifier, DEFAULT_CLASSES
from models.ingredient_classifier import IngredientClassifier, INGREDIENT_CLASSES
from models.query_assistant import QueryAssistant
from utils.recipe_engine import RecipeEngine
from utils.retrieval import ContextRetriever
from utils.location_service import LocationService
from utils.prompt_builder import PromptBuilder

# ------------------------------------------------------------------
# Page config
# ------------------------------------------------------------------
st.set_page_config(
    page_title="SmartKitchen — Cooking Assistant",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# CSS styling
# ------------------------------------------------------------------
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .recipe-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        color: white;
        margin-bottom: 1rem;
    }
    .recipe-card h3 { color: white; margin-top: 0; }
    .ingredient-badge {
        display: inline-block;
        background: #28a745;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        margin: 2px;
        font-size: 0.85rem;
    }
    .missing-badge {
        display: inline-block;
        background: #dc3545;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        margin: 2px;
        font-size: 0.85rem;
    }
    .place-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-left: 5px solid #FF6B35;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .place-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    .place-category {
        display: inline-block;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 2px 8px;
        border-radius: 4px;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    .cat-restaurant { background: #FFE8E0; color: #FF6B35; }
    .cat-grocery { background: #E0F2F1; color: #00897B; }
    
    .place-name { font-size: 1.2rem; font-weight: 700; color: #333; margin-top: 5px; }
    .place-meta { font-size: 0.9rem; color: #666; margin-top: 5px; }
    .place-rating { color: #FBC02D; font-weight: bold; margin-bottom: 5px; }
    .map-link { 
        display: inline-block; 
        margin-top: 10px; 
        font-size: 0.85rem; 
        color: #FF6B35; 
        text-decoration: none;
        font-weight: 600;
    }
    .map-link:hover { text-decoration: underline; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------
# Session state initialization
# ------------------------------------------------------------------
def auto_detect_location():
    """Fetch user's coordinates based on IP address."""
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                return data.get("lat"), data.get("lon"), data.get("city")
    except Exception:
        pass
    return 51.5074, -0.1278, "London (Default)"


def init_session_state():
    defaults = {
        "mode": "Dish Recognition",
        "chat_history": [],
        "current_context": {},
        "dish_model_loaded": False,
        "ingredient_model_loaded": False,
        "assistant_loaded": False,
        "predictions_made": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
    
    if "user_lat" not in st.session_state:
        lat, lon, city = auto_detect_location()
        st.session_state["user_lat"] = lat
        st.session_state["user_lon"] = lon
        st.session_state["user_city"] = city


init_session_state()


# ------------------------------------------------------------------
# Cached resource loading
# ------------------------------------------------------------------
@st.cache_resource
def load_recipe_engine():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return RecipeEngine(
        recipes_path=os.path.join(base, "data", "recipes.json"),
        substitutions_path=os.path.join(base, "data", "substitutions.json"),
    )


@st.cache_resource
def load_dish_model():
    model = DishClassifier(num_classes=len(DEFAULT_CLASSES), pretrained_backbone=False)
    ckpt = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "outputs", "saved_models", "dish_classifier_best.pth",
    )
    if os.path.exists(ckpt):
        model.load_pretrained(ckpt)
    else:
        model.eval()
    return model


@st.cache_resource
def load_ingredient_model():
    model = IngredientClassifier(num_classes=len(INGREDIENT_CLASSES), pretrained_backbone=False)
    ckpt = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "outputs", "saved_models", "ingredient_classifier_best.pth",
    )
    if os.path.exists(ckpt):
        model.load_pretrained(ckpt)
    else:
        model.eval()
    return model


@st.cache_resource
def load_query_assistant():
    return QueryAssistant()


@st.cache_resource
def load_location_service():
    return LocationService(use_sample_fallback=True)


# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------
def render_sidebar():
    st.sidebar.markdown("## 🍳 SmartKitchen")
    st.sidebar.markdown("---")

    mode = st.sidebar.radio(
        "Select Mode",
        ["Dish Recognition", "Ingredient Recognition"],
        index=0,
    )
    st.session_state["mode"] = mode

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📍 Your Location")
    use_location = st.sidebar.checkbox("Enable location features", value=True)

    if use_location:
        st.sidebar.caption(f"📍 Auto-detected: **{st.session_state.get('user_city', 'Unknown')}**")
        col1, col2 = st.sidebar.columns(2)
        lat = col1.number_input("Latitude", value=st.session_state["user_lat"], format="%.4f")
        lon = col2.number_input("Longitude", value=st.session_state["user_lon"], format="%.4f")
        
        # Update session state if manually adjusted
        st.session_state["user_lat"] = lat
        st.session_state["user_lon"] = lon
    else:
        lat, lon = None, None

    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Settings")
    confidence_threshold = st.sidebar.slider(
        "Confidence threshold", 0.1, 0.9, 0.5, 0.05,
        help="Minimum confidence for ingredient detection",
    )

    enable_ollama = st.sidebar.checkbox(
        "Enable Qwen (Ollama)",
        value=False,
        help="Connects to local Ollama server. Uses template fallback if unchecked.",
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "<small>SmartKitchen — MSc Deep Learning Project</small>",
        unsafe_allow_html=True,
    )

    return lat, lon, confidence_threshold, enable_ollama


# ------------------------------------------------------------------
# Dish Recognition Tab
# ------------------------------------------------------------------
def render_dish_recognition(recipe_engine, location_service, lat, lon):
    st.markdown("## 🍝 Dish Recognition")
    st.markdown("Upload a photo of a prepared meal to identify it and get recipe suggestions.")

    uploaded = st.file_uploader(
        "Upload a dish photo", type=["jpg", "jpeg", "png"], key="dish_upload"
    )

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        col1, col2 = st.columns([1, 1])

        with col1:
            st.image(image, caption="Uploaded dish", use_container_width=True)

        with col2:
            with st.spinner("Analysing dish..."):
                model = load_dish_model()
                predictions = model.predict(image, top_k=3)

            top_label, top_conf = predictions[0]
            st.success(f"**Predicted dish:** {top_label}")
            st.metric("Confidence", f"{top_conf:.1%}")

            st.markdown("#### Other possibilities")
            for label, conf in predictions[1:]:
                st.write(f"- {label}: {conf:.1%}")

        # Recipe suggestion
        st.markdown("---")
        st.markdown("### 📖 Recipe Suggestion")
        recipe = recipe_engine.get_recipe_by_dish(top_label)
        if recipe:
            render_recipe_card(recipe)
            # Update context
            st.session_state["current_context"] = ContextRetriever.build_context(
                dish=top_label,
                dish_confidence=top_conf,
                ingredients=recipe.get("ingredients"),
                recipes=[recipe],
                substitutions=recipe_engine.get_all_substitutions_for_missing(
                    recipe.get("ingredients", [])
                ),
            )
        else:
            st.info(f"No matching recipe found for '{top_label}' in database.")
            st.session_state["current_context"] = ContextRetriever.build_context(
                dish=top_label, dish_confidence=top_conf,
            )

        st.session_state["predictions_made"] = True

        # Buy Instead option
        st.markdown("---")
        if st.button("🛒 Buy Instead — Find Nearby Restaurants", key="buy_dish"):
            if lat and lon:
                restaurants = location_service.find_nearby_restaurants(lat, lon, dish=top_label)
                render_nearby_places(restaurants, "restaurant")
                st.session_state["current_context"]["nearby_places"] = restaurants
            else:
                st.warning("Enable location features in the sidebar to find nearby restaurants.")


# ------------------------------------------------------------------
# Ingredient Recognition Tab
# ------------------------------------------------------------------
def render_ingredient_recognition(recipe_engine, location_service, lat, lon, threshold):
    st.markdown("## 🥚 Ingredient Recognition")
    st.markdown("Upload a photo of pantry items or ingredients on a table.")

    uploaded = st.file_uploader(
        "Upload ingredient photo", type=["jpg", "jpeg", "png"], key="ing_upload"
    )

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        col1, col2 = st.columns([1, 1])

        with col1:
            st.image(image, caption="Uploaded ingredients", use_container_width=True)

        with col2:
            with st.spinner("Detecting ingredients..."):
                model = load_ingredient_model()
                detected = model.predict(image, threshold=threshold)
                all_probs = model.predict_all(image)

            if detected:
                st.success(f"**Detected {len(detected)} ingredient(s)**")
                for ing, conf in detected.items():
                    st.write(f"- **{ing}**: {conf:.0%}")
            else:
                st.warning("No ingredients detected above the confidence threshold.")
                st.markdown("All probabilities:")
                for ing, conf in list(all_probs.items())[:5]:
                    st.write(f"- {ing}: {conf:.0%}")

        # Recipe recommendations
        ingredient_list = list(detected.keys()) if detected else []
        if ingredient_list:
            top_ingredient = ingredient_list[0]
            st.markdown("---")
            st.markdown(f"### 📖 Recipe Recommendations for {top_ingredient.title()}")
            # Recommend based ONLY on the highest-probability ingredient
            recommendations = recipe_engine.recommend_by_ingredients([top_ingredient], top_k=3)

            for rec in recommendations:
                render_recipe_card(rec, show_score=True)

            # Missing ingredients
            if recommendations:
                top_rec = recommendations[0]
                missing = top_rec.get("missing_ingredients", [])
                if missing:
                    st.markdown("### ⚠️ Missing Ingredients")
                    for m in missing:
                        sub = recipe_engine.get_substitutions(m)
                        if sub:
                            alts = ", ".join(sub["alternatives"][:3])
                            st.write(f'- **{m}** — substitutes: {alts}')
                        else:
                            st.write(f"- **{m}**")

            # Build context
            st.session_state["current_context"] = ContextRetriever.build_context(
                ingredients=ingredient_list,
                recipes=recommendations,
                missing_ingredients=(
                    recommendations[0].get("missing_ingredients", []) if recommendations else []
                ),
                substitutions=recipe_engine.get_all_substitutions_for_missing(
                    recommendations[0].get("missing_ingredients", []) if recommendations else []
                ),
            )
            st.session_state["predictions_made"] = True

            # Nearby groceries
            st.markdown("---")
            if missing and st.button("🛒 Find Nearby Grocery Stores", key="buy_groceries"):
                if lat and lon:
                    groceries = location_service.find_nearby_groceries(lat, lon)
                    render_nearby_places(groceries, "grocery")
                    st.session_state["current_context"]["nearby_places"] = groceries
                else:
                    st.warning("Enable location features in the sidebar.")


# ------------------------------------------------------------------
# Query Assistant Tab
# ------------------------------------------------------------------
def render_query_assistant(enable_ollama: bool):
    st.markdown("## 💬 Query Assistant")
    st.markdown("Ask follow-up questions about the detected dish, ingredients, recipes, or nearby places.")

    if not st.session_state.get("predictions_made"):
        st.info("👆 First use Dish or Ingredient Recognition to generate context for the assistant.")
        return

    assistant = load_query_assistant()

    # Load model if requested
    if enable_ollama and not assistant.is_loaded:
        with st.spinner("Connecting to Ollama (this may take a moment)..."):
            try:
                assistant.load_model()
                st.success("Connected to Ollama!")
            except Exception as e:
                st.warning(f"Could not connect to Ollama: {e}. Using template-based responses.")

    # Show current context summary
    ctx = st.session_state.get("current_context", {})
    with st.expander("📋 Current session context", expanded=False):
        if "detected_dish" in ctx:
            st.write(f"**Dish:** {ctx['detected_dish']}")
        if "detected_ingredients" in ctx:
            st.write(f"**Ingredients:** {', '.join(ctx['detected_ingredients'])}")
        if "recipes" in ctx:
            st.write(f"**Recipes:** {', '.join(r['name'] for r in ctx['recipes'])}")
        if "missing_ingredients" in ctx:
            st.write(f"**Missing:** {', '.join(ctx['missing_ingredients'])}")

    # Example questions
    st.markdown("**Example questions:**")
    example_cols = st.columns(3)
    examples = [
        "What ingredients do I need?",
        "How long does this take?",
        "Can I make this vegetarian?",
        "What can I use instead of milk?",
        "What am I missing?",
        "Where can I buy the ingredients?",
    ]
    for i, ex in enumerate(examples):
        if example_cols[i % 3].button(ex, key=f"ex_{i}"):
            st.session_state["chat_history"].append({"role": "user", "content": ex})
            answer = assistant.answer(ex, ctx)
            st.session_state["chat_history"].append({"role": "assistant", "content": answer})

    # Chat history
    st.markdown("---")
    for msg in st.session_state.get("chat_history", []):
        if msg["role"] == "user":
            st.markdown(f"**🧑 You:** {msg['content']}")
        else:
            st.markdown(f"**🤖 Assistant:** {msg['content']}")

    # Input
    user_input = st.chat_input("Ask a cooking question...")
    if user_input:
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        with st.spinner("Thinking..."):
            answer = assistant.answer(user_input, ctx)
        st.session_state["chat_history"].append({"role": "assistant", "content": answer})
        st.rerun()

    if st.button("Clear chat history"):
        st.session_state["chat_history"] = []
        st.rerun()


# ------------------------------------------------------------------
# Nearby Places Tab
# ------------------------------------------------------------------
def render_nearby_places_tab(location_service, lat, lon):
    st.markdown("## 📍 Nearby Restaurants & Groceries")

    if not lat or not lon:
        st.warning("Enable location features and set coordinates in the sidebar.")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🍽️ Restaurants")
        st.caption("Find a place to eat your favorite meal.")
        dish_query = st.text_input("What are you craving?", placeholder="e.g. Pasta, Burger...", key="place_dish")
        if st.button("🔍 Search Restaurants", use_container_width=True, key="search_rest"):
            with st.spinner("Finding restaurants..."):
                restaurants = location_service.find_nearby_restaurants(lat, lon, dish=dish_query)
                render_nearby_places(restaurants, "restaurant")

    with col2:
        st.markdown("### 🛒 Grocery Stores")
        st.caption("Grab ingredients to cook it yourself.")
        st.markdown("<br>", unsafe_allow_html=True) # Spacer
        if st.button("🔍 Search Grocery Stores", use_container_width=True, key="search_groc"):
            with st.spinner("Finding groceries..."):
                groceries = location_service.find_nearby_groceries(lat, lon)
                render_nearby_places(groceries, "grocery")

    # Map placeholder
    st.markdown("---")
    st.markdown("### 🗺️ Map View")
    try:
        import folium
        from streamlit_folium import st_folium

        m = folium.Map(location=[lat, lon], zoom_start=14)
        folium.Marker([lat, lon], popup="You are here", icon=folium.Icon(color="red")).add_to(m)
        st_folium(m, width=700, height=400)
    except ImportError:
        st.info("Install `folium` and `streamlit-folium` for map visualisation: `pip install folium streamlit-folium`")


# ------------------------------------------------------------------
# Shared rendering helpers
# ------------------------------------------------------------------
def render_recipe_card(recipe: dict, show_score: bool = False):
    name = recipe.get("name", "Unknown")
    prep = recipe.get("prep_time", "N/A")
    cuisine = recipe.get("cuisine", "")
    ings = recipe.get("ingredients", [])
    steps = recipe.get("steps", [])
    score = recipe.get("score")
    matched = recipe.get("matched_ingredients", [])
    missing = recipe.get("missing_ingredients", [])

    header = f"**{name}**"
    if cuisine:
        header += f"  •  {cuisine}"
    header += f"  •  ⏱ {prep}"
    if show_score and score is not None:
        header += f"  •  Match: {score:.0%}"

    with st.container():
        st.markdown(header)

        # Ingredients
        badge_html = ""
        for ing in ings:
            if ing in matched:
                badge_html += f'<span class="ingredient-badge">✓ {ing}</span> '
            elif ing in missing:
                badge_html += f'<span class="missing-badge">✗ {ing}</span> '
            else:
                badge_html += f'<span class="ingredient-badge">{ing}</span> '
        st.markdown(badge_html, unsafe_allow_html=True)

        # Steps
        with st.expander("Cooking steps"):
            for i, step in enumerate(steps, 1):
                st.write(f"{i}. {step}")

        st.markdown("")


def render_nearby_places(places: list, category: str):
    if not places:
        st.info(f"No {category} places found.")
        return

    # Use a grid-like layout for cards
    cols = st.columns(2)
    for i, place in enumerate(places):
        name = place.get("name", "Unknown")
        dist = place.get("distance_km", "?")
        addr = place.get("address", "N/A")
        rating = place.get("rating")
        cat_class = "cat-restaurant" if category == "restaurant" else "cat-grocery"
        cat_label = "Restaurant" if category == "restaurant" else "Grocery"
        
        # Build map link
        search_query = f"{name} {addr}".replace(" ", "+")
        map_url = f"https://www.google.com/maps/search/?api=1&query={search_query}"

        rating_html = ""
        if rating:
            rating_html = f'<div class="place-rating">{"★" * int(rating)}{"☆" * (5 - int(rating))} {rating}</div>'

        with cols[i % 2]:
            st.markdown(
                f'''<div class="place-card">
<div class="place-category {cat_class}">{cat_label}</div>
{rating_html}
<div class="place-name">{name}</div>
<div class="place-meta">
📍 {addr}<br>
📏 {dist} km away
</div>
<a href="{map_url}" target="_blank" class="map-link">🔗 View on Google Maps</a>
</div>''',
                unsafe_allow_html=True,
            )


# ------------------------------------------------------------------
# Main app
# ------------------------------------------------------------------
def main():
    st.markdown('<div class="main-header">🍳 SmartKitchen</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">A Vision-Language Cooking Assistant</div>',
        unsafe_allow_html=True,
    )

    lat, lon, threshold, enable_ollama = render_sidebar()

    recipe_engine = load_recipe_engine()
    location_service = load_location_service()

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🍝 Dish Recognition",
        "🥚 Ingredient Recognition",
        "💬 Query Assistant",
        "📍 Nearby Places",
    ])

    with tab1:
        render_dish_recognition(recipe_engine, location_service, lat, lon)

    with tab2:
        render_ingredient_recognition(recipe_engine, location_service, lat, lon, threshold)

    with tab3:
        render_query_assistant(enable_ollama)

    with tab4:
        render_nearby_places_tab(location_service, lat, lon)


if __name__ == "__main__":
    main()
