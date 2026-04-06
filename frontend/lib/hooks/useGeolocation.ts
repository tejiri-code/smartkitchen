"use client";

import { useEffect } from "react";
import { useSessionContext } from "./useSessionContext";
import { autodetectLocation } from "@/lib/api/places";

export function useGeolocation() {
  const setLocation = useSessionContext((s) => s.setLocation);
  const locationEnabled = useSessionContext((s) => s.locationEnabled);

  useEffect(() => {
    if (locationEnabled) return;

    // Try browser geolocation first
    if (typeof navigator !== "undefined" && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLocation(pos.coords.latitude, pos.coords.longitude);
        },
        () => {
          // Fall back to IP-based detection
          autodetectLocation().then((res) => {
            if (res.found && res.lat != null && res.lon != null) {
              setLocation(res.lat, res.lon, res.city);
            }
          }).catch(() => {});
        },
        { timeout: 5000 },
      );
    } else {
      autodetectLocation().then((res) => {
        if (res.found && res.lat != null && res.lon != null) {
          setLocation(res.lat, res.lon, res.city);
        }
      }).catch(() => {});
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps
}
