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
import { ShoppingBasket, MapPin, RotateCcw, Loader2, Download, Zap } from "lucide-react";
import Link from "next/link";

// Sample pantry images for testing
const SAMPLE_IMAGES = [
  {
    id: 1,
    title: "Fresh Vegetables",
    url: "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=500&h=500&fit=crop",
    alt: "Fresh vegetables including tomatoes, bell peppers, and onions"
  },
  {
    id: 2,
    title: "Fresh Produce",
    url: "https://images.unsplash.com/photo-1488459716781-31db52582fe9?w=500&h=500&fit=crop",
    alt: "Fresh vegetables and fruits on display"
  },
  {
    id: 3,
    title: "Cooking Ingredients",
    url: "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500&h=500&fit=crop",
    alt: "Fresh vegetables and cooking ingredients displayed on wooden surface"
  },
  {
    id: 4,
    title: "Market Vegetables",
    url: "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=500&h=500&fit=crop",
    alt: "Colorful fresh vegetables at farmers market"
  },
];

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
  const [loadingSample, setLoadingSample] = useState<number | null>(null);

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

  async function testWithSampleImage(imageUrl: string, sampleId: number) {
    setLoadingSample(sampleId);
    try {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const file = new File([blob], "sample-image.jpg", { type: "image/jpeg" });
      await handleFile(file);
    } catch (e) {
      setError("Failed to load sample image. Please try uploading your own photo.");
    } finally {
      setLoadingSample(null);
    }
  }

  function downloadImage(imageUrl: string, title: string) {
    const link = document.createElement("a");
    link.href = imageUrl;
    link.download = `${title.toLowerCase().replace(/\s+/g, "-")}.jpg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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

      {/* Tips */}
      <AnimatePresence>
        {!result && !loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <div className="bg-blue-50 border border-blue-200 rounded-2xl p-5">
              <p className="text-sm font-semibold text-blue-900 mb-3">💡 Tips for Best Results</p>
              <ul className="text-sm text-blue-800 space-y-1.5 list-disc list-inside">
                <li><strong>Close-ups work best:</strong> Focus on individual items or shelves rather than full cabinets</li>
                <li><strong>Good lighting:</strong> Bright, natural light helps detection accuracy</li>
                <li><strong>Clear visibility:</strong> Make sure ingredient labels are visible</li>
                <li><strong>Organized layout:</strong> Items spread out are easier to detect than cluttered piles</li>
              </ul>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Example Scenarios */}
      {/* <AnimatePresence>
        {!result && !loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-3">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest">Example Pantry Scenarios</p>
            <div className="grid grid-cols-2 gap-3">
              {[
                { icon: "🧂", title: "Spices & Pantry", desc: "Organized shelves with labeled jars" },
                { icon: "🍓", title: "Fresh Produce", desc: "Vegetables and fruits on a counter" },
                { icon: "🧊", title: "Fridge Contents", desc: "Organized fridge shelves" },
                { icon: "🥫", title: "Canned Goods", desc: "Canned and boxed items" },
              ].map((scenario) => (
                <motion.div key={scenario.title} variants={item}>
                  <div className="bg-gradient-to-br from-gray-50 to-gray-100 border border-gray-200 rounded-xl p-4 text-center hover:border-gray-300 hover:shadow-md transition-all cursor-pointer">
                    <div className="text-3xl mb-2">{scenario.icon}</div>
                    <p className="text-xs font-semibold text-gray-700 mb-1">{scenario.title}</p>
                    <p className="text-xs text-gray-500">{scenario.desc}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence> */}

      {/* Try Example Images */}
      <AnimatePresence>
        {!result && !loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-3">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest">Try Example Images</p>
            <div className="grid grid-cols-2 gap-3">
              {SAMPLE_IMAGES.map((sample) => (
                <motion.div key={sample.id} variants={item} className="relative group">
                  <div className="relative w-full aspect-square rounded-xl overflow-hidden border border-gray-200 bg-gray-100 shadow-sm hover:shadow-md transition-all">
                    {/* Image */}
                    <img
                      src={sample.url}
                      alt={sample.alt}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />

                    {/* Overlay */}
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-colors duration-300 flex flex-col items-center justify-center gap-2 opacity-0 group-hover:opacity-100">
                      <button
                        onClick={() => testWithSampleImage(sample.url, sample.id)}
                        disabled={loadingSample === sample.id}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-white text-gray-900 rounded-lg text-xs font-semibold hover:bg-gray-100 disabled:opacity-50 transition-all"
                      >
                        {loadingSample === sample.id ? <Loader2 size={12} className="animate-spin" /> : <Zap size={12} />}
                        {loadingSample === sample.id ? "Testing..." : "Test This"}
                      </button>
                      <button
                        onClick={() => downloadImage(sample.url, sample.title)}
                        className="flex items-center gap-1.5 px-3 py-1.5 bg-white text-gray-900 rounded-lg text-xs font-semibold hover:bg-gray-100 transition-all"
                      >
                        <Download size={12} /> Download
                      </button>
                    </div>

                    {/* Label */}
                    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent px-3 py-2 group-hover:from-black/40">
                      <p className="text-xs font-semibold text-white">{sample.title}</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
            <p className="text-xs text-gray-500 text-center">Click "Test This" to instantly classify a sample, or "Download" to use offline</p>
          </motion.div>
        )}
      </AnimatePresence>

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
