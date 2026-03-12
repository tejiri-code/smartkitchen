import { motion } from "framer-motion";
import type { Place } from "@/lib/types";
import { formatDistance, formatRating } from "@/lib/utils/formatters";
import { MapPin, Star, Navigation2 } from "lucide-react";

interface Props {
  place: Place;
}

export default function PlaceCard({ place }: Props) {
  const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(place.name + " " + place.address)}`;

  return (
    <motion.a
      href={mapsUrl}
      target="_blank"
      rel="noopener noreferrer"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      className="block bg-white border border-gray-100 rounded-2xl p-4 transition-all duration-200"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h3 className="font-semibold text-gray-900 truncate text-sm">{place.name}</h3>
          <p className="text-xs text-gray-500 mt-0.5 truncate flex items-center gap-1">
            <MapPin size={12} /> {place.address}
          </p>
        </div>

        <div className="text-right shrink-0">
          <p className="text-xs font-bold text-orange-600 flex items-center justify-end gap-0.5">
            <Navigation2 size={12} /> {formatDistance(place.distance_km)}
          </p>
          {place.rating != null && (
            <p className="text-xs text-amber-500 font-semibold mt-0.5 flex items-center justify-end gap-0.5">
              <Star size={12} fill="currentColor" /> {formatRating(place.rating)}
            </p>
          )}
        </div>
      </div>

      {/* Category badge */}
      <div className="mt-3 pt-3 border-t border-gray-100 flex items-center gap-2">
        <span className="text-xs font-medium text-gray-500 bg-gray-100 px-2 py-1 rounded-full capitalize">
          {place.category}
        </span>
        <span className="text-xs text-orange-500 font-medium ml-auto hover:underline cursor-pointer transition-colors">
          View on Maps ↗
        </span>
      </div>
    </motion.a>
  );
}
