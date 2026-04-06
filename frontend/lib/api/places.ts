import { get } from "./client";
import type { PlacesResponse, GeocodeResponse, AutodetectResponse } from "@/lib/types";

export function getRestaurants(
  lat: number,
  lon: number,
  dish = "",
  radiusKm = 3.0,
  limit = 5,
): Promise<PlacesResponse> {
  const params = new URLSearchParams({
    lat: String(lat),
    lon: String(lon),
    dish,
    radius_km: String(radiusKm),
    limit: String(limit),
  });
  return get<PlacesResponse>(`/places/restaurants?${params}`);
}

export function getGroceries(
  lat: number,
  lon: number,
  radiusKm = 3.0,
  limit = 5,
): Promise<PlacesResponse> {
  const params = new URLSearchParams({
    lat: String(lat),
    lon: String(lon),
    radius_km: String(radiusKm),
    limit: String(limit),
  });
  return get<PlacesResponse>(`/places/groceries?${params}`);
}

export function geocodeAddress(address: string): Promise<GeocodeResponse> {
  return get<GeocodeResponse>(`/places/geocode?address=${encodeURIComponent(address)}`);
}

export function autodetectLocation(): Promise<AutodetectResponse> {
  return get<AutodetectResponse>("/places/autodetect");
}
