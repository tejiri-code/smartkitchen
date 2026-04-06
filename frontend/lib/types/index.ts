// ---- Recipes ----

export interface Recipe {
  name: string;
  ingredients: string[];
  steps: string[];
  prep_time: string;
  cuisine: string;
  category: string;
  match_score?: number;
}

export interface RecipeWithScore extends Recipe {
  score: number;
  matched_ingredients: string[];
  missing_ingredients: string[];
}

// ---- Dish classification ----

export interface DishPrediction {
  label: string;
  confidence: number;
}

export interface DishResponse {
  predictions: DishPrediction[];
  top_label: string;
  top_confidence: number;
}

export interface DishRecipeResponse extends DishResponse {
  recipe: Recipe | null;
  context: AssistantContext;
}

// ---- Ingredient classification ----

export interface IngredientResponse {
  detected: Record<string, number>;
  all_probabilities?: Record<string, number>;
  count: number;
}

export interface IngredientRecommendResponse extends IngredientResponse {
  recommendations: RecipeWithScore[];
  context: AssistantContext;
}

// ---- Substitutions ----

export interface SubstitutionResponse {
  ingredient: string;
  alternatives: string[];
  notes: string;
}

// ---- Places ----

export interface Place {
  name: string;
  distance_km: number;
  address: string;
  rating: number | null;
  category: string;
}

export interface PlacesResponse {
  places: Place[];
}

// ---- Assistant / chat ----

export interface ChatTurn {
  question: string;
  answer: string;
}

export interface AssistantContext {
  detected_dish?: string;
  dish_confidence?: number;
  detected_ingredients?: string[];
  recipes?: RecipeWithScore[];
  missing_ingredients?: string[];
  substitutions?: SubstitutionResponse[];
  nearby_places?: Place[];
  [key: string]: unknown;
}

export interface AskRequest {
  question: string;
  context: AssistantContext;
  history: ChatTurn[];
  use_ollama: boolean;
  image?: string;
}

export interface AskResponse {
  answer: string;
  used_model: boolean;
}

// ---- Location ----

export interface GeocodeResponse {
  lat?: number;
  lon?: number;
  found: boolean;
}

export interface AutodetectResponse {
  lat?: number;
  lon?: number;
  city?: string;
  found: boolean;
}

// ---- Feedback ----

export interface RecipeFeedback {
  recipe_name: string;
  rating: number; // 1 = helpful, -1 = not helpful
}

export interface ChatFeedback {
  question: string;
  answer: string;
  helpful: boolean;
}
