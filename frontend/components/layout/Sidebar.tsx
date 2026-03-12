"use client";

import { useSessionContext } from "@/lib/hooks/useSessionContext";
import { geocodeAddress } from "@/lib/api/places";
import { useState } from "react";

export default function Sidebar() {
  const {
    userCity, userLat, userLon, locationEnabled,
    confidenceThreshold, useOllama,
    setLocation, setThreshold, setUseOllama,
  } = useSessionContext();

  const [addressInput, setAddressInput] = useState("");
  const [geocoding, setGeocoding] = useState(false);

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
    <aside className="w-64 shrink-0 bg-white border-r border-gray-200 p-4 flex flex-col gap-5 overflow-y-auto">
      <div>
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Location</h3>
        {locationEnabled && (
          <p className="text-xs text-green-600 mb-2">
            {userCity || `${userLat.toFixed(2)}, ${userLon.toFixed(2)}`}
          </p>
        )}
        <div className="flex gap-1">
          <input
            type="text"
            value={addressInput}
            onChange={(e) => setAddressInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleGeocode()}
            placeholder="Enter city or address"
            className="flex-1 text-xs border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-1"
            style={{ "--tw-ring-color": "#FF6B35" } as React.CSSProperties}
          />
          <button
            onClick={handleGeocode}
            disabled={geocoding}
            className="text-xs px-2 py-1 rounded text-white disabled:opacity-50 cursor-pointer"
            style={{ backgroundColor: "#FF6B35" }}
          >
            {geocoding ? "..." : "Go"}
          </button>
        </div>
      </div>

      <div>
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
          Confidence Threshold: {Math.round(confidenceThreshold * 100)}%
        </h3>
        <input
          type="range"
          min={0.1}
          max={0.9}
          step={0.05}
          value={confidenceThreshold}
          onChange={(e) => setThreshold(parseFloat(e.target.value))}
          className="w-full accent-orange-500"
        />
        <div className="flex justify-between text-xs text-gray-400 mt-0.5">
          <span>10%</span>
          <span>90%</span>
        </div>
      </div>

      <div>
        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">AI Model</h3>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={useOllama}
            onChange={(e) => setUseOllama(e.target.checked)}
            className="accent-orange-500"
          />
          <span className="text-xs text-gray-700">Use Qwen (Ollama)</span>
        </label>
        <p className="text-xs text-gray-400 mt-1">
          Requires Ollama running locally.
        </p>
      </div>
    </aside>
  );
}
