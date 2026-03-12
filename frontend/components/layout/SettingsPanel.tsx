"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useSessionContext } from "@/lib/hooks/useSessionContext";
import { geocodeAddress } from "@/lib/api/places";
import { MapPin, Sliders, Loader2 } from "lucide-react";

interface Props {
  onClose: () => void;
}

export default function SettingsPanel({ onClose }: Props) {
  const {
    userCity, userLat, userLon, locationEnabled,
    confidenceThreshold, useOllama, autoDetectLocation,
    setLocation, setThreshold, setUseOllama, setAutoDetectLocation,
  } = useSessionContext();

  const [addressInput, setAddressInput] = useState(userCity || "");
  const [geocoding, setGeocoding] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);

  // Close on click outside
  useEffect(() => {
    function handler(e: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        onClose();
      }
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [onClose]);

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

  return (
    <div
      ref={panelRef}
      className="absolute right-0 top-full mt-2 w-80 bg-white border border-gray-100 rounded-2xl shadow-lg z-50 p-5 space-y-5"
    >
      {/* Location */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <MapPin size={16} className="text-orange-500" />
          <p className="text-xs font-semibold text-gray-700 uppercase tracking-widest">Location</p>
        </div>
        {locationEnabled && (
          <p className="text-xs text-emerald-600 font-medium mb-2">
            📍 {userCity || `${userLat.toFixed(2)}°, ${userLon.toFixed(2)}°`}
          </p>
        )}
        <div className="flex gap-2">
          <input
            type="text"
            value={addressInput}
            onChange={(e) => setAddressInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleGeocode()}
            placeholder="City or address"
            className="flex-1 text-xs border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-1 focus:ring-orange-400 transition-all"
          />
          <button
            onClick={handleGeocode}
            disabled={geocoding}
            className="text-xs px-3 py-2 rounded-lg text-white disabled:opacity-50 cursor-pointer shrink-0 font-medium transition-all hover:shadow-md"
            style={{ backgroundColor: "#FF7A18" }}
          >
            {geocoding ? <Loader2 size={14} className="inline animate-spin" /> : "Set"}
          </button>
        </div>
      </div>

      {/* Divider */}
      <div className="h-px bg-gray-100" />

      {/* Threshold */}
      <div>
        <div className="flex justify-between items-center mb-3">
          <p className="text-xs font-semibold text-gray-700 uppercase tracking-widest">Confidence</p>
          <span className="text-xs font-bold text-orange-600 bg-orange-50 px-2 py-1 rounded-full">
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
        <p className="text-[10px] text-gray-400 mt-2">
          How confident the AI needs to be before making predictions
        </p>
      </div>

      {/* Divider */}
      <div className="h-px bg-gray-100" />

      {/* Ollama model */}
      <div>
        <label className="flex items-start gap-3 cursor-pointer group">
          <input
            type="checkbox"
            checked={useOllama}
            onChange={(e) => setUseOllama(e.target.checked)}
            className="accent-orange-500 w-4 h-4 mt-0.5 cursor-pointer"
          />
          <div className="flex-1">
            <p className="text-xs font-semibold text-gray-700">Use Qwen (Ollama)</p>
            <p className="text-[10px] text-gray-400 mt-0.5">
              Run AI locally for better recipe answers. Requires Ollama installed.
            </p>
          </div>
        </label>
      </div>

      {/* Auto-detect location */}
      <div>
        <label className="flex items-start gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={autoDetectLocation}
            onChange={(e) => setAutoDetectLocation(e.target.checked)}
            className="accent-orange-500 w-4 h-4 mt-0.5 cursor-pointer"
          />
          <div className="flex-1">
            <p className="text-xs font-semibold text-gray-700">Auto-detect location</p>
            <p className="text-[10px] text-gray-400 mt-0.5">
              Use your device location for nearby places
            </p>
          </div>
        </label>
      </div>

      {/* Divider */}
      <div className="h-px bg-gray-100" />

      {/* More settings link */}
      <Link
        href="/settings"
        onClick={onClose}
        className="flex items-center justify-between w-full px-3 py-2.5 rounded-lg text-xs font-semibold text-orange-600 bg-orange-50 hover:bg-orange-100 transition-colors cursor-pointer group"
      >
        <span className="flex items-center gap-2">
          <Sliders size={14} /> Full Settings
        </span>
        <span className="text-orange-400 group-hover:translate-x-1 transition-transform">→</span>
      </Link>
    </div>
  );
}
