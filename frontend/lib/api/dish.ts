import { postForm } from "./client";
import type { DishResponse, DishRecipeResponse } from "@/lib/types";

export function classifyDish(file: File, topK = 3): Promise<DishResponse> {
  const form = new FormData();
  form.append("file", file);
  return postForm<DishResponse>(`/classify/dish?top_k=${topK}`, form);
}

export function classifyDishWithRecipe(file: File, topK = 3): Promise<DishRecipeResponse> {
  const form = new FormData();
  form.append("file", file);
  return postForm<DishRecipeResponse>(`/classify/dish/with-recipe?top_k=${topK}`, form);
}
