"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useSessionContext } from "@/lib/hooks/useSessionContext";
import { useGeolocation } from "@/lib/hooks/useGeolocation";
import { classifyIngredientsWithRecipes } from "@/lib/api/ingredients";
import { getGroceries } from "@/lib/api/places";
import type { IngredientRecommendResponse, Place } from "@/lib/types";
import ImageInputCard from "@/components/shared/ImageInputCard";
import ErrorMessage from "@/components/shared/ErrorMessage";
import IngredientBadge from "@/components/shared/IngredientBadge";
import RecipeCard from "@/components/shared/RecipeCard";
import PlaceList from "@/components/places/PlaceList";
import { ShoppingBasket, MapPin, RotateCcw, Loader2 } from "lucide-react";
import Link from "next/link";

const fade = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4 } },
};

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.04 } },
};

const item = { hidden: { opacity: 0, scale: 0.9 }, show: { opacity: 1, scale: 1 } };

export default function IngredientsPage() {
  useGeolocation();

  const { confidenceThreshold, userLat, userLon, setIngredientContext } = useSessionContext();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<IngredientRecommendResponse | null>(null);
  const [places, setPlaces] = useState<Place[] | null>(null);
  const [loadingPlaces, setLoadingPlaces] = useState(false);

  async function handleFile(file: File) {
    setLoading(true);
    setError(null);
    setResult(null);
    setPlaces(null);
    try {
      const data = await classifyIngredientsWithRecipes(file, confidenceThreshold, 3);
      setResult(data);
      setIngredientContext(data.context);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Classification failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleFindGroceries() {
    setLoadingPlaces(true);
    try {
      const res = await getGroceries(userLat, userLon, 3.0, 5);
      setPlaces(res.places);
    } catch {
      setPlaces([]);
    } finally {
      setLoadingPlaces(false);
    }
  }

  function reset() {
    setResult(null);
    setPlaces(null);
  }

  const missingIngredients = result?.recommendations[0]?.missing_ingredients ?? [];

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center text-white"
               style={{ background: "linear-gradient(135deg, #34A853, #4CAF6A)" }}>
            <ShoppingBasket size={20} strokeWidth={2} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Ingredient Detection</h1>
            <p className="text-sm text-gray-500">Scan your pantry to find recipes and discover what you can cook.</p>
          </div>
        </div>
        {result && (
          <button onClick={reset} className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 transition-colors cursor-pointer">
            <RotateCcw size={14} /> Reset
          </button>
        )}
      </div>

      {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}

      {/* Upload / camera */}
      <AnimatePresence>
        {!result && !loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <ImageInputCard onFile={handleFile} label="Upload a pantry or ingredients photo" hint="show your cupboard, fridge, or ingredients" />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading */}
      {loading && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center gap-3 py-16">
          <div className="w-14 h-14 rounded-2xl flex items-center justify-center shadow-lg"
               style={{ background: "linear-gradient(135deg, #34A853, #4CAF6A)" }}>
            <Loader2 size={26} className="text-white animate-spin" />
          </div>
          <p className="text-sm font-semibold text-gray-800">Detecting ingredients…</p>
          <p className="text-xs text-gray-400">Scanning and analysing your pantry</p>
        </motion.div>
      )}

      {/* Results */}
      <AnimatePresence>
        {result && (
          <motion.div variants={fade} initial="hidden" animate="show" className="space-y-6">
            {/* Detected ingredients */}
            <motion.div className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest">Detected Ingredients</p>
                <span className="text-xs font-semibold text-gray-500 bg-gray-100 px-2 py-1 rounded-full">{result.count}</span>
              </div>

              {result.count === 0 ? (
                <p className="text-sm text-gray-500">No ingredients detected. Try a clearer photo or lower the confidence threshold in Settings.</p>
              ) : (
                <motion.div variants={container} initial="hidden" animate="show" className="flex flex-wrap gap-2">
                  {Object.entries(result.detected).map(([name, conf]) => (
                    <motion.div key={name} variants={item}>
                      <IngredientBadge name={name} variant="detected" confidence={conf} />
                    </motion.div>
                  ))}
                </motion.div>
              )}
            </motion.div>

            {/* Recipe recommendations */}
            {result.recommendations.length > 0 && (
              <motion.div variants={fade} className="space-y-4">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest">
                  Recipes You Can Make
                </p>
                <div className="grid grid-cols-1 gap-3">
                  {result.recommendations.slice(0, 3).map((rec, i) => (
                    <motion.div key={rec.name} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
                      <RecipeCard recipe={rec} showScore />
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Missing ingredients alert */}
            {missingIngredients.length > 0 && (
              <motion.div variants={fade} className="bg-red-50 border border-red-200 rounded-2xl p-5 space-y-3">
                <p className="text-sm font-semibold text-red-800">Missing for Top Recipe</p>
                <motion.div variants={container} initial="hidden" animate="show" className="flex flex-wrap gap-2">
                  {missingIngredients.map((ing) => (
                    <motion.div key={ing} variants={item}>
                      <IngredientBadge name={ing} variant="missing" />
                    </motion.div>
                  ))}
                </motion.div>

                <button
                  onClick={handleFindGroceries}
                  disabled={loadingPlaces}
                  className="w-full mt-3 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-semibold text-white disabled:opacity-50 cursor-pointer transition-all hover:shadow-lg"
                  style={{ background: "linear-gradient(135deg, #34A853, #4CAF6A)" }}
                >
                  {loadingPlaces ? <Loader2 size={16} className="animate-spin" /> : <MapPin size={16} />}
                  {loadingPlaces ? "Finding stores…" : "Find Nearby Grocery Stores"}
                </button>
              </motion.div>
            )}

            {/* Nearby grocery stores */}
            {places !== null && (
              <motion.div variants={fade}>
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">Nearby Grocery Stores</p>
                <PlaceList places={places} />
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
