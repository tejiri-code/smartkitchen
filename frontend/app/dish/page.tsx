"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useSessionContext } from "@/lib/hooks/useSessionContext";
import { useGeolocation } from "@/lib/hooks/useGeolocation";
import { classifyDishWithRecipe } from "@/lib/api/dish";
import { getRestaurants } from "@/lib/api/places";
import type { DishRecipeResponse, Place } from "@/lib/types";
import ImageInputCard from "@/components/shared/ImageInputCard";
import ErrorMessage from "@/components/shared/ErrorMessage";
import RecipeCard from "@/components/shared/RecipeCard";
import PlaceList from "@/components/places/PlaceList";
import { ChefHat, MapPin, MessageSquare, Loader2, RotateCcw } from "lucide-react";
import Link from "next/link";

const fade = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4 } },
};

export default function DishPage() {
  useGeolocation();

  const { userLat, userLon, setDishContext } = useSessionContext();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<DishRecipeResponse | null>(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState<string | null>(null);
  const [places, setPlaces] = useState<Place[] | null>(null);
  const [loadingPlaces, setLoadingPlaces] = useState(false);

  async function handleFile(file: File) {
    setLoading(true);
    setError(null);
    setResult(null);
    setPlaces(null);
    setImagePreviewUrl(URL.createObjectURL(file));
    try {
      const data = await classifyDishWithRecipe(file, 3);
      setResult(data);
      setDishContext(data.context);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Classification failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleFindRestaurants() {
    if (!result) return;
    setLoadingPlaces(true);
    try {
      const res = await getRestaurants(userLat, userLon, result.top_label, 3.0, 5);
      setPlaces(res.places);
    } catch {
      setPlaces([]);
    } finally {
      setLoadingPlaces(false);
    }
  }

  function reset() {
    setResult(null);
    setImagePreviewUrl(null);
    setPlaces(null);
    setError(null);
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center text-white"
               style={{ background: "linear-gradient(135deg, #FF7A18, #FF9A4A)" }}>
            <ChefHat size={20} strokeWidth={2} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Dish Recognition</h1>
            <p className="text-sm text-gray-500">Upload or capture a food photo to identify and get recipes.</p>
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
            <ImageInputCard onFile={handleFile} label="Upload a dish photo" hint="or drag & drop your food image" />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading */}
      {loading && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center gap-3 py-16">
          <div className="w-14 h-14 rounded-2xl flex items-center justify-center shadow-lg"
               style={{ background: "linear-gradient(135deg, #FF7A18, #FF9A4A)" }}>
            <Loader2 size={26} className="text-white animate-spin" />
          </div>
          <p className="text-sm font-semibold text-gray-800">Analysing your dish…</p>
          <p className="text-xs text-gray-400">Running AI recognition model</p>
        </motion.div>
      )}

      {/* Results */}
      <AnimatePresence>
        {result && (
          <motion.div variants={fade} initial="hidden" animate="show" className="space-y-6">
            {/* Two-col: image + predictions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {imagePreviewUrl && (
                <div className="rounded-2xl overflow-hidden border border-gray-100 shadow-sm bg-white">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={imagePreviewUrl} alt="Uploaded dish" className="w-full h-56 object-cover" />
                  <div className="px-4 py-3 flex items-center justify-between">
                    <p className="text-xs text-gray-400">Uploaded photo</p>
                    <button onClick={reset} className="text-xs text-orange-500 hover:underline cursor-pointer">Try another</button>
                  </div>
                </div>
              )}

              {/* Predictions card */}
              <div className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-4">Predictions</p>
                <div className="space-y-4">
                  {result.predictions.map((pred, i) => (
                    <motion.div key={pred.label} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.08 }}>
                      <div className="flex items-center justify-between text-sm mb-1.5">
                        <span className={i === 0 ? "font-semibold text-gray-900" : "text-gray-600"}>{pred.label}</span>
                        <span className={[
                          "text-xs font-semibold px-2 py-0.5 rounded-full",
                          i === 0 ? "bg-orange-100 text-orange-600" : "bg-gray-100 text-gray-500",
                        ].join(" ")}>
                          {Math.round(pred.confidence * 100)}%
                        </span>
                      </div>
                      <div className="h-1.5 rounded-full bg-gray-100 overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${pred.confidence * 100}%` }}
                          transition={{ delay: i * 0.08 + 0.2, duration: 0.6, ease: "easeOut" }}
                          className="h-full rounded-full"
                          style={{ background: i === 0 ? "linear-gradient(90deg, #FF7A18, #FF9A4A)" : "#E5E7EB" }}
                        />
                      </div>
                    </motion.div>
                  ))}
                </div>
                <div className="mt-5 pt-4 border-t border-gray-100">
                  <p className="text-xs text-gray-400 mb-1">Best match</p>
                  <span className="inline-flex items-center gap-1.5 text-sm font-semibold text-gray-900">
                    <ChefHat size={14} className="text-orange-500" /> {result.top_label}
                  </span>
                </div>
              </div>
            </div>

            {/* Recipe */}
            {result.recipe ? (
              <motion.div variants={fade} className="space-y-4">
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest">Matched Recipe</p>
                <RecipeCard recipe={result.recipe} />
                <div className="flex flex-col sm:flex-row gap-3">
                  <button
                    onClick={handleFindRestaurants}
                    disabled={loadingPlaces}
                    className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-semibold text-white disabled:opacity-50 cursor-pointer transition-all hover:shadow-lg hover:shadow-orange-200"
                    style={{ background: "linear-gradient(135deg, #FF7A18, #FF9A4A)" }}
                  >
                    {loadingPlaces ? <Loader2 size={16} className="animate-spin" /> : <MapPin size={16} />}
                    {loadingPlaces ? "Finding restaurants…" : "Find Nearby Restaurants"}
                  </button>
                  <Link
                    href="/assistant"
                    className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-semibold text-gray-700 border border-gray-200 bg-white hover:bg-gray-50 transition-colors"
                  >
                    <MessageSquare size={16} /> Ask AI Assistant
                  </Link>
                </div>
              </motion.div>
            ) : (
              <div className="bg-amber-50 border border-amber-200 rounded-2xl px-5 py-4 flex items-start gap-3">
                <ChefHat size={18} className="text-amber-500 mt-0.5 shrink-0" />
                <div>
                  <p className="text-sm font-medium text-amber-800">No recipe found for <strong>{result.top_label}</strong></p>
                  <p className="text-xs text-amber-600 mt-0.5">Try asking the AI Assistant for suggestions.</p>
                </div>
              </div>
            )}

            {places !== null && (
              <motion.div variants={fade}>
                <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">Nearby Restaurants</p>
                <PlaceList places={places} />
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
