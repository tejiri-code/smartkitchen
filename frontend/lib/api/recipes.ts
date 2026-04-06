import { get, post } from "./client";
import type { RecipeWithScore, SubstitutionResponse } from "@/lib/types";

interface RecipeByDishResponse {
  recipe: import("@/lib/types").Recipe | null;
}

interface RecommendResponse {
  recommendations: RecipeWithScore[];
}

export function getRecipeByDish(dish: string): Promise<RecipeByDishResponse> {
  return get<RecipeByDishResponse>(`/recipes/by-dish?dish=${encodeURIComponent(dish)}`);
}

export function recommendByIngredients(
  available_ingredients: string[],
  top_k = 3,
): Promise<RecommendResponse> {
  return post<RecommendResponse>("/recipes/recommend", { available_ingredients, top_k });
}

export function getSubstitutions(ingredient: string): Promise<SubstitutionResponse> {
  return get<SubstitutionResponse>(
    `/recipes/substitutions?ingredient=${encodeURIComponent(ingredient)}`,
  );
}
