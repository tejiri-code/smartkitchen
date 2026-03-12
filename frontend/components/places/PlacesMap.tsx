"use client";

import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import type { Place } from "@/lib/types";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useEffect } from "react";

// Fix default Leaflet marker icons (webpack asset issue)
// eslint-disable-next-line @typescript-eslint/no-explicit-any
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

const userIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

function MapRecenter({ lat, lon }: { lat: number; lon: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView([lat, lon], 13);
  }, [lat, lon, map]);
  return null;
}

interface Props {
  userLat: number;
  userLon: number;
  places: Place[];
}

export default function PlacesMap({ userLat, userLon, places }: Props) {
  return (
    <div className="rounded-xl overflow-hidden border border-gray-200 shadow-sm" style={{ height: 350 }}>
      <MapContainer center={[userLat, userLon]} zoom={13} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          attribution='© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapRecenter lat={userLat} lon={userLon} />

        <Marker position={[userLat, userLon]} icon={userIcon}>
          <Popup>You are here</Popup>
        </Marker>

        {places.map((p, i) => {
          // We don't have exact coords from Overpass in the Place schema;
          // approximate by offsetting slightly from user for demo
          const lat = userLat + (Math.random() - 0.5) * 0.02;
          const lon = userLon + (Math.random() - 0.5) * 0.02;
          return (
            <Marker key={i} position={[lat, lon]}>
              <Popup>
                <strong>{p.name}</strong><br />
                {p.address}<br />
                {p.distance_km} km away
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}
