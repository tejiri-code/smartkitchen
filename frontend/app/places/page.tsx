"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useSessionContext } from "@/lib/hooks/useSessionContext";
import { useGeolocation } from "@/lib/hooks/useGeolocation";
import { getRestaurants, getGroceries } from "@/lib/api/places";
import type { Place } from "@/lib/types";
import ErrorMessage from "@/components/shared/ErrorMessage";
import PlaceList from "@/components/places/PlaceList";
import dynamic from "next/dynamic";
import { MapPin, Utensils, ShoppingBag, Loader2, RotateCcw } from "lucide-react";

const PlacesMap = dynamic(() => import("@/components/places/PlacesMap"), { ssr: false });

const fade = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4 } },
};

export default function PlacesPage() {
  useGeolocation();

  const { userLat, userLon } = useSessionContext();
  const [dishQuery, setDishQuery] = useState("");
  const [restaurants, setRestaurants] = useState<Place[] | null>(null);
  const [groceries, setGroceries] = useState<Place[] | null>(null);
  const [loadingR, setLoadingR] = useState(false);
  const [loadingG, setLoadingG] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const allPlaces = [...(restaurants ?? []), ...(groceries ?? [])];

  async function handleRestaurants() {
    setLoadingR(true);
    setError(null);
    try {
      const res = await getRestaurants(userLat, userLon, dishQuery, 3.0, 5);
      setRestaurants(res.places);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Search failed.");
    } finally {
      setLoadingR(false);
    }
  }

  async function handleGroceries() {
    setLoadingG(true);
    setError(null);
    try {
      const res = await getGroceries(userLat, userLon, 3.0, 5);
      setGroceries(res.places);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Search failed.");
    } finally {
      setLoadingG(false);
    }
  }

  function reset() {
    setRestaurants(null);
    setGroceries(null);
    setDishQuery("");
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center text-white"
               style={{ background: "linear-gradient(135deg, #EC4899, #F43F5E)" }}>
            <MapPin size={20} strokeWidth={2} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Nearby Places</h1>
            <p className="text-sm text-gray-500">Discover restaurants and grocery stores in your area.</p>
          </div>
        </div>
        {(restaurants || groceries) && (
          <button onClick={reset} className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-800 transition-colors cursor-pointer">
            <RotateCcw size={14} /> Reset
          </button>
        )}
      </div>

      {error && <ErrorMessage message={error} onDismiss={() => setError(null)} />}

      {/* Search cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Restaurants search */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-6 h-6 rounded-lg flex items-center justify-center text-white text-sm"
                 style={{ background: "linear-gradient(135deg, #FF7A18, #FF9A4A)" }}>
              <Utensils size={14} strokeWidth={2.5} />
            </div>
            <h2 className="text-sm font-semibold text-gray-900">Find Restaurants</h2>
          </div>
          <input
            type="text"
            value={dishQuery}
            onChange={(e) => setDishQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleRestaurants()}
            placeholder="Search by dish name (optional)"
            className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 mb-3 focus:outline-none focus:ring-1 focus:ring-orange-300 transition-all"
          />
          <button
            onClick={handleRestaurants}
            disabled={loadingR}
            className="w-full py-2.5 rounded-lg text-sm font-semibold text-white disabled:opacity-50 cursor-pointer transition-all hover:shadow-lg"
            style={{ background: "linear-gradient(135deg, #FF7A18, #FF9A4A)" }}
          >
            {loadingR ? (
              <span className="flex items-center justify-center gap-2">
                <Loader2 size={14} className="animate-spin" /> Searching…
              </span>
            ) : (
              "Find Restaurants"
            )}
          </button>
        </motion.div>

        {/* Grocery stores search */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }} className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-6 h-6 rounded-lg flex items-center justify-center text-white text-sm"
                 style={{ background: "linear-gradient(135deg, #34A853, #4CAF6A)" }}>
              <ShoppingBag size={14} strokeWidth={2.5} />
            </div>
            <h2 className="text-sm font-semibold text-gray-900">Find Grocery Stores</h2>
          </div>
          <p className="text-xs text-gray-400 mb-3">Supermarkets and grocery stores near you.</p>
          <button
            onClick={handleGroceries}
            disabled={loadingG}
            className="w-full py-2.5 rounded-lg text-sm font-semibold text-white disabled:opacity-50 cursor-pointer transition-all hover:shadow-lg"
            style={{ background: "linear-gradient(135deg, #34A853, #4CAF6A)" }}
          >
            {loadingG ? (
              <span className="flex items-center justify-center gap-2">
                <Loader2 size={14} className="animate-spin" /> Searching…
              </span>
            ) : (
              "Find Grocery Stores"
            )}
          </button>
        </motion.div>
      </div>

      {/* Results */}
      <AnimatePresence>
        {restaurants !== null && (
          <motion.div variants={fade} initial="hidden" animate="show">
            <div className="flex items-center gap-2 mb-4">
              <Utensils size={16} className="text-orange-500" />
              <h2 className="text-sm font-semibold text-gray-900">Restaurants Nearby</h2>
              <span className="ml-auto text-xs text-gray-400">{restaurants.length} results</span>
            </div>
            {restaurants.length === 0 ? (
              <div className="bg-gray-50 border border-gray-200 rounded-2xl px-4 py-6 text-center">
                <p className="text-sm text-gray-500">No restaurants found in your area.</p>
              </div>
            ) : (
              <PlaceList places={restaurants} />
            )}
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {groceries !== null && (
          <motion.div variants={fade} initial="hidden" animate="show">
            <div className="flex items-center gap-2 mb-4">
              <ShoppingBag size={16} className="text-emerald-500" />
              <h2 className="text-sm font-semibold text-gray-900">Grocery Stores Nearby</h2>
              <span className="ml-auto text-xs text-gray-400">{groceries.length} results</span>
            </div>
            {groceries.length === 0 ? (
              <div className="bg-gray-50 border border-gray-200 rounded-2xl px-4 py-6 text-center">
                <p className="text-sm text-gray-500">No grocery stores found in your area.</p>
              </div>
            ) : (
              <PlaceList places={groceries} />
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Map */}
      <AnimatePresence>
        {allPlaces.length > 0 && (
          <motion.div variants={fade} initial="hidden" animate="show">
            <h2 className="text-sm font-semibold text-gray-900 mb-4">Map View</h2>
            <div className="rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
              <PlacesMap userLat={userLat} userLon={userLon} places={allPlaces} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
