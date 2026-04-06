import { postForm } from "./client";
import type { IngredientResponse, IngredientRecommendResponse } from "@/lib/types";

export function classifyIngredients(
  file: File,
  threshold = 0.5,
  includeAll = false,
): Promise<IngredientResponse> {
  const form = new FormData();
  form.append("file", file);
  return postForm<IngredientResponse>(
    `/classify/ingredients?threshold=${threshold}&include_all=${includeAll}`,
    form,
  );
}

export function classifyIngredientsWithRecipes(
  file: File,
  threshold = 0.5,
  topK = 3,
): Promise<IngredientRecommendResponse> {
  const form = new FormData();
  form.append("file", file);
  return postForm<IngredientRecommendResponse>(
    `/classify/ingredients/with-recipes?threshold=${threshold}&top_k=${topK}`,
    form,
  );
}
