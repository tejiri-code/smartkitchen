export function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`;
}

export function formatDistance(km: number): string {
  return `${km.toFixed(1)} km`;
}

export function formatRating(rating: number | null): string {
  if (rating == null) return "—";
  return `${rating.toFixed(1)} ★`;
}

export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}
