from typing import List, Optional
from pydantic import BaseModel


class Place(BaseModel):
    name: str
    distance_km: float
    address: str
    rating: Optional[float] = None
    category: str


class PlacesResponse(BaseModel):
    places: List[Place]


class GeocodeResponse(BaseModel):
    lat: Optional[float] = None
    lon: Optional[float] = None
    found: bool


class AutodetectResponse(BaseModel):
    lat: Optional[float] = None
    lon: Optional[float] = None
    city: Optional[str] = None
    found: bool
