"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useSessionContext } from "@/lib/hooks/useSessionContext";
import { useGeolocation } from "@/lib/hooks/useGeolocation";
import { geocodeAddress } from "@/lib/api/places";
import {
  Settings, MapPin, Zap, Wand2, Camera, Loader2,
  Gauge, Radio, MapPinOff, Trash2, ChevronRight,Clock
} from "lucide-react";

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.06 } },
};

const item = { hidden: { opacity: 0, x: -12 }, show: { opacity: 1, x: 0 } };

export default function SettingsPage() {
  useGeolocation();

  const {
    userLat, userLon, userCity, locationEnabled, autoDetectLocation,
    confidenceThreshold, useOllama, defaultImageSource, resultsPerPage,
    recipeHistory, setLocation, setThreshold, setUseOllama, setAutoDetectLocation,
    setDefaultImageSource, setResultsPerPage, clearCache, clearChat, clearRecipeHistory,
  } = useSessionContext();

  const [addressInput, setAddressInput] = useState(userCity || "");
  const [geocoding, setGeocoding] = useState(false);
  const [cleared, setCleared] = useState(false);

  async function handleGeocode() {
    if (!addressInput.trim()) return;
    setGeocoding(true);
    try {
      const res = await geocodeAddress(addressInput);
      if (res.found && res.lat != null && res.lon != null) {
        setLocation(res.lat, res.lon, addressInput);
      }
    } finally {
      setGeocoding(false);
    }
  }

  function handleClearCache() {
    clearCache();
    clearChat();
    setCleared(true);
    setTimeout(() => setCleared(false), 3000);
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center text-white shadow-md"
             style={{ background: "linear-gradient(135deg, #FF7A18, #FF9A4A)" }}>
          <Settings size={20} strokeWidth={2} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-sm text-gray-500">Customize your SmartKitchen experience</p>
        </div>
      </div>

      <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
        {/* Location Settings */}
        <motion.div variants={item} className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <MapPin size={18} className="text-orange-500" />
            <h2 className="text-base font-bold text-gray-900">Location & Places</h2>
          </div>

          {/* Current location */}
          {locationEnabled && (
            <div className="mb-4 p-3 bg-emerald-50 border border-emerald-200 rounded-lg">
              <p className="text-xs text-emerald-700 font-medium">
                📍 Current Location: <span className="font-bold">{userCity || `${userLat.toFixed(2)}°, ${userLon.toFixed(2)}°`}</span>
              </p>
            </div>
          )}

          {/* Set location */}
          <div className="space-y-2 mb-4">
            <label className="text-xs font-semibold text-gray-700">Set Manual Location</label>
            <div className="flex gap-2">
              <input
                type="text"
                value={addressInput}
                onChange={(e) => setAddressInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleGeocode()}
                placeholder="City, address, or zip code"
                className="flex-1 text-sm border border-gray-200 rounded-lg px-3 py-2.5 focus:outline-none focus:ring-1 focus:ring-orange-400 transition-all"
              />
              <button
                onClick={handleGeocode}
                disabled={geocoding}
                className="text-sm px-4 py-2.5 rounded-lg text-white disabled:opacity-50 cursor-pointer font-medium transition-all hover:shadow-md"
                style={{ backgroundColor: "#FF7A18" }}
              >
                {geocoding ? <Loader2 size={16} className="inline animate-spin" /> : "Set"}
              </button>
            </div>
          </div>

          {/* Auto-detect toggle */}
          <label className="flex items-start gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={autoDetectLocation}
              onChange={(e) => setAutoDetectLocation(e.target.checked)}
              className="accent-orange-500 w-4 h-4 mt-1 cursor-pointer"
            />
            <div>
              <p className="text-sm font-medium text-gray-700">Auto-detect location</p>
              <p className="text-xs text-gray-500 mt-0.5">Use device location when available</p>
            </div>
          </label>
        </motion.div>

        {/* Recognition Settings */}
        <motion.div variants={item} className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Zap size={18} className="text-yellow-500" />
            <h2 className="text-base font-bold text-gray-900">Recognition & AI</h2>
          </div>

          {/* Confidence threshold */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <label className="text-sm font-semibold text-gray-700">Confidence Threshold</label>
              <span className="text-sm font-bold text-orange-600 bg-orange-50 px-3 py-1 rounded-full">
                {Math.round(confidenceThreshold * 100)}%
              </span>
            </div>
            <input
              type="range"
              min={0.1}
              max={0.9}
              step={0.05}
              value={confidenceThreshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="w-full h-2 accent-orange-500 cursor-pointer rounded-lg"
            />
            <p className="text-xs text-gray-500 mt-2">
              Higher = more certain predictions. Adjust if getting unexpected results.
            </p>
          </div>

          {/* Ollama toggle */}
          <label className="flex items-start gap-3 cursor-pointer p-3 bg-indigo-50 border border-indigo-200 rounded-lg">
            <input
              type="checkbox"
              checked={useOllama}
              onChange={(e) => setUseOllama(e.target.checked)}
              className="accent-indigo-600 w-4 h-4 mt-1 cursor-pointer"
            />
            <div className="flex-1">
              <p className="text-sm font-medium text-indigo-900">Use Qwen (Ollama) for AI</p>
              <p className="text-xs text-indigo-700 mt-0.5">Run local AI model for better recipe suggestions</p>
              <p className="text-xs text-indigo-600 mt-1">
                {useOllama ? "✓ Enabled" : "○ Disabled"} — Requires Ollama installation
              </p>
            </div>
          </label>
        </motion.div>

        {/* Image Input Settings */}
        <motion.div variants={item} className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Camera size={18} className="text-blue-500" />
            <h2 className="text-base font-bold text-gray-900">Image Input</h2>
          </div>

          <label className="text-sm font-semibold text-gray-700 mb-3 block">Default Image Source</label>
          <div className="space-y-2">
            {(["upload", "camera"] as const).map((source) => (
              <label
                key={source}
                className={[
                  "flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all",
                  defaultImageSource === source
                    ? "bg-blue-50 border-blue-200"
                    : "bg-gray-50 border-gray-200 hover:border-gray-300",
                ].join(" ")}
              >
                <input
                  type="radio"
                  name="imageSource"
                  checked={defaultImageSource === source}
                  onChange={() => setDefaultImageSource(source)}
                  className="w-4 h-4 accent-blue-500 cursor-pointer"
                />
                <div className="flex-1">
                  <p className={`text-sm font-medium ${defaultImageSource === source ? "text-blue-900" : "text-gray-700"}`}>
                    {source === "upload" ? "Upload from Device" : "Capture with Camera"}
                  </p>
                  <p className={`text-xs mt-0.5 ${defaultImageSource === source ? "text-blue-600" : "text-gray-500"}`}>
                    {source === "upload"
                      ? "Browse and select files from your device"
                      : "Use your device camera to capture photos"}
                  </p>
                </div>
              </label>
            ))}
          </div>
        </motion.div>

        {/* Results Settings */}
        <motion.div variants={item} className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Gauge size={18} className="text-green-500" />
            <h2 className="text-base font-bold text-gray-900">Results & Display</h2>
          </div>

          <label className="text-sm font-semibold text-gray-700 mb-3 block">Results Per Page</label>
          <div className="flex items-center gap-4">
            <input
              type="range"
              min={3}
              max={20}
              step={1}
              value={resultsPerPage}
              onChange={(e) => setResultsPerPage(parseInt(e.target.value))}
              className="flex-1 h-2 accent-green-500 cursor-pointer rounded-lg"
            />
            <span className="text-sm font-bold text-green-600 bg-green-50 px-3 py-1 rounded-full w-12 text-center">
              {resultsPerPage}
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-2">How many results to display per page</p>
        </motion.div>

        {/* Recipe History */}
        <motion.div variants={item} className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Clock size={18} className="text-purple-500" />
            <h2 className="text-base font-bold text-gray-900">Recipe History</h2>
          </div>

          {recipeHistory.length > 0 ? (
            <>
              <div className="space-y-2 mb-4 max-h-64 overflow-y-auto">
                {recipeHistory.map((item, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 bg-purple-50 border border-purple-100 rounded-lg"
                  >
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{item.name}</p>
                      <p className="text-xs text-gray-500">
                        {new Date(item.timestamp).toLocaleDateString()} at{" "}
                        {new Date(item.timestamp).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              <button
                onClick={clearRecipeHistory}
                className="w-full px-4 py-3 rounded-lg text-sm font-semibold transition-all bg-purple-50 text-purple-700 border border-purple-200 hover:bg-purple-100"
              >
                Clear History
              </button>
              <p className="text-xs text-gray-500 mt-2">
                {recipeHistory.length} recipe{recipeHistory.length !== 1 ? "s" : ""} viewed
              </p>
            </>
          ) : (
            <div className="text-center py-8">
              <p className="text-sm text-gray-500">No recipe history yet</p>
              <p className="text-xs text-gray-400 mt-1">
                Recipes you view will appear here
              </p>
            </div>
          )}
        </motion.div>

        {/* Data & Cache */}
        <motion.div variants={item} className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-4">
            <Trash2 size={18} className="text-red-500" />
            <h2 className="text-base font-bold text-gray-900">Data & Cache</h2>
          </div>

          <button
            onClick={handleClearCache}
            className={[
              "w-full px-4 py-3 rounded-lg text-sm font-semibold transition-all",
              cleared
                ? "bg-green-50 text-green-700 border border-green-200"
                : "bg-red-50 text-red-700 border border-red-200 hover:bg-red-100",
            ].join(" ")}
          >
            {cleared ? "✓ Cache cleared" : "Clear all cached data"}
          </button>
          <p className="text-xs text-gray-500 mt-2">
            Clears detection history, chat messages, and cached recipes
          </p>
        </motion.div>

        {/* Info */}
        <motion.div variants={item} className="bg-gradient-to-r from-gray-50 to-gray-100 border border-gray-200 rounded-2xl p-6">
          <p className="text-xs text-gray-600 leading-relaxed">
            <strong>💡 Tip:</strong> Settings are saved locally in your browser. They sync across tabs but won't transfer to other devices.
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
}
