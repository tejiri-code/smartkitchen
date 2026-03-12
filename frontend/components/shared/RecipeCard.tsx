import { motion } from "framer-motion";
import type { Recipe, RecipeWithScore } from "@/lib/types";
import IngredientBadge from "./IngredientBadge";
import { Clock, Globe, ChefHat } from "lucide-react";

interface Props {
  recipe: Recipe | RecipeWithScore;
  showScore?: boolean;
}

function isWithScore(r: Recipe | RecipeWithScore): r is RecipeWithScore {
  return "score" in r && "matched_ingredients" in r;
}

export default function RecipeCard({ recipe, showScore = false }: Props) {
  const withScore = isWithScore(recipe) ? recipe : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white border border-gray-100 rounded-2xl shadow-sm overflow-hidden transition-all duration-200 hover:shadow-md hover:border-gray-200"
    >
      {/* Header */}
      <div className="px-5 py-4 border-b border-gray-100">
        <div className="flex items-start justify-between gap-3 mb-2">
          <h3 className="font-bold text-gray-900 text-base leading-tight flex-1">{recipe.name}</h3>
          {showScore && withScore && (
            <motion.span
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="shrink-0 text-xs font-bold text-white bg-gradient-to-r from-emerald-500 to-teal-500 px-2.5 py-1 rounded-full whitespace-nowrap"
            >
              {Math.round(withScore.score * 100)}% match
            </motion.span>
          )}
        </div>

        {/* Meta tags */}
        <div className="flex flex-wrap gap-2">
          <span className="text-xs text-gray-500 bg-gray-100 rounded-full px-2.5 py-1 flex items-center gap-1">
            <Clock size={12} /> {recipe.prep_time}
          </span>
          <span className="text-xs text-gray-500 bg-gray-100 rounded-full px-2.5 py-1 flex items-center gap-1">
            <Globe size={12} /> {recipe.cuisine}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="px-5 py-4 space-y-4">
        {/* Ingredients */}
        <div>
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2">Ingredients</p>
          <div className="flex flex-wrap gap-1.5">
            {recipe.ingredients.map((ing) => {
              const variant =
                withScore?.matched_ingredients.includes(ing) ? "matched"
                : withScore?.missing_ingredients.includes(ing) ? "missing"
                : "detected";
              return (
                <IngredientBadge
                  key={ing}
                  name={ing}
                  variant={withScore ? variant : "detected"}
                />
              );
            })}
          </div>
        </div>

        {/* Steps */}
        {recipe.steps.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2">Cooking Steps</p>
            <ol className="text-sm text-gray-700 space-y-1.5">
              {recipe.steps.slice(0, 3).map((step, i) => (
                <li key={i} className="list-decimal list-inside leading-snug">
                  <span className="text-gray-600">{step}</span>
                </li>
              ))}
              {recipe.steps.length > 3 && (
                <li className="text-xs text-gray-400 list-none ml-6">
                  + {recipe.steps.length - 3} more step{recipe.steps.length - 3 !== 1 ? "s" : ""}
                </li>
              )}
            </ol>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-5 py-3 border-t border-gray-100 bg-gray-50 flex items-center gap-2 text-xs text-gray-500">
        <ChefHat size={12} /> {recipe.category}
      </div>
    </motion.div>
  );
}
