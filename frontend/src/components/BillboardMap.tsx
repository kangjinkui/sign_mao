import { useEffect, useRef, useState } from "react";

import { loadKakaoMaps } from "../services/kakaoMapLoader";
import type { RadiusItem } from "../types/radius";
import { formatAdType } from "../utils/adTypeLabel";

type Props = {
  center?: { lat: number; lng: number };
  radius: number;
  items: RadiusItem[];
};

export function BillboardMap({ center, radius, items }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<any>(null);
  const circleRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);
  const infoWindowsRef = useRef<any[]>([]);
  const [mapError, setMapError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const renderMap = async () => {
      if (!containerRef.current) return;
      try {
        const kakao = await loadKakaoMaps();
        if (cancelled || !containerRef.current) return;

        const defaultCenter = new kakao.maps.LatLng(37.5173, 127.0473);
        if (!mapRef.current) {
          mapRef.current = new kakao.maps.Map(containerRef.current, {
            center: defaultCenter,
            level: 5,
          });
        }

        const map = mapRef.current;
        if (!map) return;

        const centerLatLng = center
          ? new kakao.maps.LatLng(center.lat, center.lng)
          : new kakao.maps.LatLng(37.5173, 127.0473);
        map.setCenter(centerLatLng);
        map.setLevel(5);

        if (circleRef.current) {
          circleRef.current.setMap(null);
        }
        circleRef.current = new kakao.maps.Circle({
          center: centerLatLng,
          radius,
          strokeWeight: 2,
          strokeColor: "#0f766e",
          strokeOpacity: 0.9,
          fillColor: "#5eead4",
          fillOpacity: 0.25,
        });
        circleRef.current.setMap(map);

        for (const marker of markersRef.current) {
          marker.setMap(null);
        }
        for (const infoWindow of infoWindowsRef.current) {
          infoWindow.close();
        }
        markersRef.current = items.map((item) => {
          const marker = new kakao.maps.Marker({
            position: new kakao.maps.LatLng(item.lat, item.lng),
          });
          marker.setMap(map);
          const infoWindow = new (kakao as any).maps.InfoWindow({
            content: `<div style="padding:8px;max-width:260px;line-height:1.4;">
              <div><strong>광고물 종류</strong>: ${formatAdType(item.ad_type)}</div>
              <div><strong>표시주소</strong>: ${item.address}</div>
            </div>`,
          });
          (kakao as any).maps.event.addListener(marker, "click", () => {
            for (const opened of infoWindowsRef.current) {
              opened.close();
            }
            infoWindow.open(map, marker);
          });
          infoWindowsRef.current.push(infoWindow);
          return marker;
        });
        setMapError(null);
      } catch (error) {
        const err = error as Error;
        setMapError(err.message);
      }
    };

    void renderMap();
    return () => {
      cancelled = true;
    };
  }, [center?.lat, center?.lng, items, radius]);

  return (
    <section aria-label="billboard-map" style={{ border: "1px solid #ddd", padding: 12 }}>
      <strong>반경 지도</strong>
      <div>중심: {center ? `${center.lat}, ${center.lng}` : "강남구청(기본값)"}</div>
      <div>반경: {radius}m</div>
      <div>마커 수: {items.length}</div>
      {mapError && (
        <p role="alert" style={{ color: "#b91c1c", marginTop: 8 }}>
          지도 로딩 오류: {mapError}
        </p>
      )}
      <div
        ref={containerRef}
        style={{ width: "100%", height: 360, marginTop: 10, borderRadius: 8, overflow: "hidden" }}
      />
    </section>
  );
}
