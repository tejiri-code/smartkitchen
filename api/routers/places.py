import requests
from fastapi import APIRouter, Query
from api.dependencies import get_location_service
from api.schemas.places import PlacesResponse, Place, GeocodeResponse, AutodetectResponse

router = APIRouter()


@router.get("/restaurants", response_model=PlacesResponse)
def get_restaurants(
    lat: float = Query(...),
    lon: float = Query(...),
    dish: str = Query(default=""),
    radius_km: float = Query(default=3.0),
    limit: int = Query(default=5),
):
    svc = get_location_service()
    raw = svc.find_nearby_restaurants(lat, lon, dish=dish, radius_km=radius_km, limit=limit)
    return PlacesResponse(places=[Place(**p) for p in raw])


@router.get("/groceries", response_model=PlacesResponse)
def get_groceries(
    lat: float = Query(...),
    lon: float = Query(...),
    radius_km: float = Query(default=3.0),
    limit: int = Query(default=5),
):
    svc = get_location_service()
    raw = svc.find_nearby_groceries(lat, lon, radius_km=radius_km, limit=limit)
    return PlacesResponse(places=[Place(**p) for p in raw])


@router.get("/geocode", response_model=GeocodeResponse)
def geocode(address: str = Query(...)):
    svc = get_location_service()
    result = svc.geocode_address(address)
    if result is None:
        return GeocodeResponse(found=False)
    return GeocodeResponse(lat=result[0], lon=result[1], found=True)


@router.get("/autodetect", response_model=AutodetectResponse)
def autodetect_location():
    """Detect approximate location via IP geolocation (ip-api.com)."""
    try:
        resp = requests.get("http://ip-api.com/json/", timeout=5)
        data = resp.json()
        if data.get("status") == "success":
            return AutodetectResponse(
                lat=data.get("lat"),
                lon=data.get("lon"),
                city=data.get("city"),
                found=True,
            )
    except Exception:
        pass
    return AutodetectResponse(found=False)
