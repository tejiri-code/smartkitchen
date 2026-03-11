"""
Location Service
================
Finds nearby restaurants and grocery stores using the free OpenStreetMap
Overpass API (no API key required).  Falls back to sample data when the
API is unreachable so the demo always works.
"""

import math
import requests
from typing import List, Dict, Optional, Tuple

try:
    from geopy.geocoders import Nominatim
    from geopy.distance import geodesic

    _HAS_GEOPY = True
except ImportError:
    _HAS_GEOPY = False


# ------------------------------------------------------------------
# Sample fallback data (used when API is unavailable or for demo mode)
# ------------------------------------------------------------------
_SAMPLE_RESTAURANTS = [
    {"name": "Bella Pasta", "distance_km": 0.8, "address": "12 High Street", "rating": 4.3, "category": "restaurant"},
    {"name": "Roma Kitchen", "distance_km": 1.2, "address": "45 Park Lane", "rating": 4.1, "category": "restaurant"},
    {"name": "Golden Dragon", "distance_km": 1.5, "address": "78 Market Road", "rating": 4.5, "category": "restaurant"},
    {"name": "Spice House", "distance_km": 2.0, "address": "3 Station Avenue", "rating": 4.2, "category": "restaurant"},
    {"name": "The Local Grill", "distance_km": 2.3, "address": "99 Church Street", "rating": 4.0, "category": "restaurant"},
]

_SAMPLE_GROCERIES = [
    {"name": "FreshMart", "distance_km": 0.5, "address": "22 Mill Lane", "rating": 4.0, "category": "grocery"},
    {"name": "Tesco Express", "distance_km": 0.9, "address": "15 High Street", "rating": 3.8, "category": "grocery"},
    {"name": "Aldi", "distance_km": 1.4, "address": "60 London Road", "rating": 4.1, "category": "grocery"},
    {"name": "Sainsbury's Local", "distance_km": 1.8, "address": "8 Queen Street", "rating": 3.9, "category": "grocery"},
]


class LocationService:
    """Find nearby restaurants and grocery stores."""

    OVERPASS_URL = "https://overpass-api.de/api/interpreter"

    def __init__(self, use_sample_fallback: bool = True):
        self.use_sample_fallback = use_sample_fallback

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def find_nearby_restaurants(
        self,
        lat: float,
        lon: float,
        dish: str = "",
        radius_km: float = 3.0,
        limit: int = 5,
    ) -> List[Dict]:
        """Search for restaurants near (lat, lon).

        If *dish* is provided it is used as a keyword hint (best-effort).
        Falls back to sample data if the Overpass query fails.
        """
        try:
            results = self._overpass_query(
                lat, lon, radius_km, amenity="restaurant"
            )
            if results:
                places = self._parse_overpass(results, lat, lon, "restaurant")
                return sorted(places, key=lambda p: p["distance_km"])[:limit]
        except Exception:
            pass

        if self.use_sample_fallback:
            return _SAMPLE_RESTAURANTS[:limit]
        return []

    def find_nearby_groceries(
        self,
        lat: float,
        lon: float,
        radius_km: float = 3.0,
        limit: int = 5,
    ) -> List[Dict]:
        """Search for grocery stores / supermarkets near (lat, lon)."""
        try:
            results = self._overpass_query(
                lat, lon, radius_km, shop="supermarket"
            )
            if results:
                places = self._parse_overpass(results, lat, lon, "grocery")
                return sorted(places, key=lambda p: p["distance_km"])[:limit]
        except Exception:
            pass

        if self.use_sample_fallback:
            return _SAMPLE_GROCERIES[:limit]
        return []

    # ------------------------------------------------------------------
    # Geocoding
    # ------------------------------------------------------------------
    @staticmethod
    def geocode_address(address: str) -> Optional[Tuple[float, float]]:
        """Convert a street address to (lat, lon) using Nominatim.

        Returns ``None`` if geopy is not installed or geocoding fails.
        """
        if not _HAS_GEOPY:
            return None
        try:
            geolocator = Nominatim(user_agent="smartkitchen_app")
            location = geolocator.geocode(address, timeout=10)
            if location:
                return (location.latitude, location.longitude)
        except Exception:
            pass
        return None

    # ------------------------------------------------------------------
    # Overpass API helpers
    # ------------------------------------------------------------------
    def _overpass_query(
        self,
        lat: float,
        lon: float,
        radius_km: float,
        amenity: str = "",
        shop: str = "",
    ) -> list:
        """Run an Overpass QL query and return the raw element list."""
        radius_m = int(radius_km * 1000)

        filters = []
        if amenity:
            filters.append(f'["amenity"="{amenity}"]')
        if shop:
            filters.append(f'["shop"="{shop}"]')

        filter_str = "".join(filters)
        query = (
            f"[out:json][timeout:10];"
            f"("
            f"  node{filter_str}(around:{radius_m},{lat},{lon});"
            f"  way{filter_str}(around:{radius_m},{lat},{lon});"
            f");"
            f"out center;"
        )
        resp = requests.get(
            self.OVERPASS_URL,
            params={"data": query},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json().get("elements", [])

    def _parse_overpass(
        self,
        elements: list,
        user_lat: float,
        user_lon: float,
        category: str,
    ) -> List[Dict]:
        """Convert Overpass elements into a uniform place dict list."""
        places = []
        for el in elements:
            # Get coordinates (node → lat/lon, way → center)
            lat = el.get("lat") or el.get("center", {}).get("lat")
            lon = el.get("lon") or el.get("center", {}).get("lon")
            if lat is None or lon is None:
                continue

            tags = el.get("tags", {})
            name = tags.get("name", "Unknown")
            address_parts = [
                tags.get("addr:housenumber", ""),
                tags.get("addr:street", ""),
                tags.get("addr:city", ""),
            ]
            address = " ".join(p for p in address_parts if p).strip() or "Address not available"

            dist = self._haversine(user_lat, user_lon, lat, lon)

            places.append(
                {
                    "name": name,
                    "distance_km": round(dist, 1),
                    "address": address,
                    "rating": None,  # Overpass doesn't have ratings
                    "category": category,
                }
            )
        return places

    # ------------------------------------------------------------------
    # Distance calculation
    # ------------------------------------------------------------------
    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Return distance in km between two coordinate pairs."""
        R = 6371.0  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ======================================================================
# Quick self-test
# ======================================================================
if __name__ == "__main__":
    svc = LocationService(use_sample_fallback=True)

    # London coordinates for demo
    lat, lon = 51.5074, -0.1278

    print("=== Nearby Restaurants ===")
    for place in svc.find_nearby_restaurants(lat, lon, dish="pasta"):
        print(f"  {place['name']} — {place['distance_km']} km — {place['address']}")

    print("\n=== Nearby Grocery Stores ===")
    for place in svc.find_nearby_groceries(lat, lon):
        print(f"  {place['name']} — {place['distance_km']} km — {place['address']}")
