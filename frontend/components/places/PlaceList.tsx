import type { Place } from "@/lib/types";
import PlaceCard from "./PlaceCard";

interface Props {
  places: Place[];
}

export default function PlaceList({ places }: Props) {
  if (places.length === 0) {
    return <p className="text-sm text-gray-500">No places found nearby.</p>;
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {places.map((place, i) => (
        <PlaceCard key={i} place={place} />
      ))}
    </div>
  );
}
