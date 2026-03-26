import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import type { Recipe, RecipeWithScore } from "@/lib/types";
import { useSessionContext } from "@/lib/hooks/useSessionContext";
import { submitRecipeFeedback } from "@/lib/api/feedback";
import IngredientBadge from "./IngredientBadge";
import { Clock, Globe, ChefHat, ChevronDown, ThumbsUp, ThumbsDown } from "lucide-react";

interface Props {
  recipe: Recipe | RecipeWithScore;
  showScore?: boolean;
}

function isWithScore(r: Recipe | RecipeWithScore): r is RecipeWithScore {
  return "score" in r && "matched_ingredients" in r;
}

export default function RecipeCard({ recipe, showScore = false }: Props) {
  const [expandedSteps, setExpandedSteps] = useState(false);
  const [userRating, setUserRating] = useState<number | null>(null);
  const { addRecipeToHistory, rateRecipe, recipeFeedback } = useSessionContext();
  const withScore = isWithScore(recipe) ? recipe : null;

  // Track recipe view in history
  useEffect(() => {
    addRecipeToHistory(recipe.name);
  }, [recipe.name, addRecipeToHistory]);

  // Check if user has already rated this recipe
  useEffect(() => {
    const existingRating = recipeFeedback[recipe.name];
    if (existingRating !== undefined) {
      setUserRating(existingRating);
    }
  }, [recipe.name, recipeFeedback]);

  const handleRating = async (rating: number) => {
    try {
      await submitRecipeFeedback({
        recipe_name: recipe.name,
        rating: rating,
      });
      setUserRating(rating);
      rateRecipe(recipe.name, rating);
    } catch (error) {
      console.error("Failed to submit recipe feedback:", error);
    }
  };

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
              {recipe.steps.slice(0, expandedSteps ? recipe.steps.length : 3).map((step, i) => (
                <li key={i} className="list-decimal list-inside leading-snug">
                  <span className="text-gray-600">{step}</span>
                </li>
              ))}
            </ol>
            {recipe.steps.length > 3 && (
              <button
                onClick={() => setExpandedSteps(!expandedSteps)}
                className="mt-2 text-xs text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1 transition-colors"
              >
                <ChevronDown size={14} className={`transition-transform ${expandedSteps ? "rotate-180" : ""}`} />
                {expandedSteps
                  ? "Show less"
                  : `+ ${recipe.steps.length - 3} more step${recipe.steps.length - 3 !== 1 ? "s" : ""}`}
              </button>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-5 py-3 border-t border-gray-100 bg-gray-50 flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <ChefHat size={12} /> {recipe.category}
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={() => handleRating(1)}
            className={`p-1.5 rounded-lg transition-colors ${
              userRating === 1
                ? "bg-emerald-100 text-emerald-600"
                : "hover:bg-gray-100 text-gray-400 hover:text-gray-600"
            }`}
            title="Helpful"
          >
            <ThumbsUp size={14} />
          </button>
          <button
            onClick={() => handleRating(-1)}
            className={`p-1.5 rounded-lg transition-colors ${
              userRating === -1
                ? "bg-red-100 text-red-600"
                : "hover:bg-gray-100 text-gray-400 hover:text-gray-600"
            }`}
            title="Not helpful"
          >
            <ThumbsDown size={14} />
          </button>
        </div>
      </div>
    </motion.div>
  );
}
