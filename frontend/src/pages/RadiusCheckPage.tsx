import { useCallback, useEffect, useRef, useState } from "react";

import { AddressSearchForm } from "../components/AddressSearchForm";
import { AdminPanel } from "../components/AdminPanel";
import { BillboardForm } from "../components/BillboardForm";
import { BillboardMap } from "../components/BillboardMap";
import { listBillboards, deleteBillboard, toRadiusItem } from "../services/billboardsApi";
import { geocodeAddress } from "../services/kakaoGeocoder";
import { RadiusResultList } from "../components/RadiusResultList";
import type { GeocodeCandidate, RadiusItem } from "../types/radius";

const RADIUS_M = 200;
const IS_STANDALONE = import.meta.env.VITE_STANDALONE === "true";

function toRadians(degree: number): number {
  return (degree * Math.PI) / 180;
}

function distanceMeters(a: { lat: number; lng: number }, b: { lat: number; lng: number }): number {
  const earthRadius = 6_371_000;
  const dLat = toRadians(b.lat - a.lat);
  const dLng = toRadians(b.lng - a.lng);
  const lat1 = toRadians(a.lat);
  const lat2 = toRadians(b.lat);
  const h =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
  return 2 * earthRadius * Math.asin(Math.sqrt(h));
}

export function RadiusCheckPage() {
  const isMountedRef = useRef(true);
  const [loading, setLoading] = useState(false);
  const [dbLoading, setDbLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchCenter, setSearchCenter] = useState<{ lat: number; lng: number } | null>(null);
  const [pendingAddress, setPendingAddress] = useState<string | null>(null);
  const [candidates, setCandidates] = useState<GeocodeCandidate[]>([]);
  const [dbMarkers, setDbMarkers] = useState<RadiusItem[]>([]);
  const [filteredItems, setFilteredItems] = useState<RadiusItem[]>([]);
  const [showAllItems, setShowAllItems] = useState(false);
  const [focusedItem, setFocusedItem] = useState<RadiusItem | null>(null);
  const [lastDbLoadedAt, setLastDbLoadedAt] = useState<Date | null>(null);
  const [dbSourceCount, setDbSourceCount] = useState(0);

  // admin state
  const [adminMode, setAdminMode] = useState(false);
  const [adminSecret, setAdminSecret] = useState("");
  const [formItem, setFormItem] = useState<RadiusItem | "new" | null>(null);

  const loadDbMarkers = useCallback(async () => {
    if (!isMountedRef.current) return;
    setDbLoading(true);
    try {
      const resp = await listBillboards(200);
      setDbSourceCount(resp.count);
      const uniqueAddressItems = resp.items.filter(
        (item, index, arr) => arr.findIndex((target) => target.address === item.address) === index
      );
      const pairs: RadiusItem[] = [];
      for (const item of uniqueAddressItems) {
        if (typeof item.lat === "number" && typeof item.lng === "number") {
          pairs.push(toRadiusItem(item, item.lat, item.lng));
        } else {
          const cands = await geocodeAddress(item.address);
          if (cands.length > 0) {
            pairs.push(toRadiusItem(item, cands[0].lat, cands[0].lng));
          }
        }
        await new Promise((resolve) => setTimeout(resolve, 40));
      }
      if (!isMountedRef.current) return;
      setDbMarkers(pairs);
      setLastDbLoadedAt(new Date());
      if (resp.count > 0 && pairs.length === 0) {
        setError("DB 데이터는 조회됐지만 주소 지오코딩에 실패했습니다. Kakao 키/도메인 설정을 확인하세요.");
      } else {
        setError(null);
      }
    } catch {
      if (!isMountedRef.current) return;
      setDbMarkers([]);
    } finally {
      if (!isMountedRef.current) return;
      setDbLoading(false);
    }
  }, []);

  useEffect(() => {
    isMountedRef.current = true;

    const run = async () => {
      try {
        await loadDbMarkers();
      } catch {
        // no-op
      }
    };

    void run();
    const timer = setInterval(() => {
      void run();
    }, 30_000);

    return () => {
      isMountedRef.current = false;
      clearInterval(timer);
    };
  }, [loadDbMarkers]);

  const runSearch = async (address: string, selectedCandidateId?: string) => {
    setLoading(true);
    setError(null);
    setFocusedItem(null);
    setShowAllItems(false);

    try {
      const geocodeCandidates = await geocodeAddress(address);
      if (geocodeCandidates.length === 0) {
        setError("지오코딩 결과가 없습니다.");
        setSearchCenter(null);
        setFilteredItems([]);
        return;
      }

      if (!selectedCandidateId && geocodeCandidates.length > 1) {
        setCandidates(geocodeCandidates.slice(0, 5));
        setPendingAddress(address);
        setSearchCenter(null);
        setFilteredItems([]);
        return;
      }

      const selected =
        geocodeCandidates.find((candidate) => candidate.candidate_id === selectedCandidateId) ??
        geocodeCandidates[0];
      const center = { lat: selected.lat, lng: selected.lng };
      const withinRadius = dbMarkers
        .map((item) => ({
          ...item,
          distance_m: distanceMeters(center, { lat: item.lat, lng: item.lng }),
        }))
        .filter((item) => item.distance_m <= RADIUS_M)
        .sort((a, b) => a.distance_m - b.distance_m);

      setSearchCenter(center);
      setFilteredItems(withinRadius);
      setCandidates([]);
      setPendingAddress(null);
    } catch (caught) {
      const err = caught as Error & { details?: { geocode_candidates?: GeocodeCandidate[] } };
      const candidateList = err.details?.geocode_candidates ?? [];
      if (candidateList.length > 0) {
        setCandidates(candidateList);
        setPendingAddress(address);
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAdminModeChange = (active: boolean, secret: string) => {
    setAdminMode(active);
    setAdminSecret(secret);
  };

  const handleDelete = async (item: RadiusItem) => {
    if (!confirm(`"${item.company}" 광고물을 삭제하시겠습니까?`)) return;
    try {
      await deleteBillboard(item.id, adminSecret);
      await loadDbMarkers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "삭제 실패");
    }
  };

  const handleFormSaved = async () => {
    setFormItem(null);
    await loadDbMarkers();
  };

  return (
    <main style={{ maxWidth: 900, margin: "0 auto", padding: 24, display: "grid", gap: 16 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <h1 style={{ margin: 0 }}>대형광고물 200m 반경 판정</h1>
        {!IS_STANDALONE && <AdminPanel adminMode={adminMode} onAdminModeChange={handleAdminModeChange} />}
      </div>
      <AddressSearchForm onSearch={(address) => void runSearch(address)} loading={loading} />
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        {!IS_STANDALONE && (
          <button type="button" onClick={() => void loadDbMarkers()} disabled={dbLoading}>
            {dbLoading ? "DB 데이터 새로고침 중..." : "DB 데이터 새로고침"}
          </button>
        )}
        <small>
          {IS_STANDALONE ? `내장 데이터 (${dbSourceCount}건)` : `마지막 갱신: ${lastDbLoadedAt ? lastDbLoadedAt.toLocaleTimeString("ko-KR") : "아직 없음"}`}
        </small>
        {!IS_STANDALONE && <small>DB 원본 건수: {dbSourceCount}</small>}
        {!IS_STANDALONE && adminMode && (
          <button type="button" onClick={() => setFormItem("new")} style={{ marginLeft: "auto" }}>
            + 광고물 등록
          </button>
        )}
      </div>

      {candidates.length > 0 && pendingAddress && (
        <section>
          <h2>지오코딩 후보 선택</h2>
          <ul>
            {candidates.map((candidate) => (
              <li key={candidate.candidate_id}>
                <button onClick={() => void runSearch(pendingAddress, candidate.candidate_id)}>
                  {candidate.address}
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}

      {error && <p role="alert">오류: {error}</p>}

      <div style={{ display: "flex", gap: 8 }}>
        <button type="button" onClick={() => setShowAllItems(true)}>
          전체 업소 정보 표시
        </button>
        <button type="button" onClick={() => setShowAllItems(false)}>
          반경 200m 결과 보기
        </button>
      </div>

      <BillboardMap
        center={focusedItem ? { lat: focusedItem.lat, lng: focusedItem.lng } : searchCenter ?? undefined}
        radius={RADIUS_M}
        items={showAllItems ? dbMarkers : filteredItems}
      />
      <RadiusResultList
        items={showAllItems ? dbMarkers : filteredItems}
        onMoveToMap={(item) => setFocusedItem(item)}
        adminMode={IS_STANDALONE ? false : adminMode}
        onEdit={(item) => setFormItem(item)}
        onDelete={(item) => void handleDelete(item)}
      />

      {formItem !== null && (
        <BillboardForm
          item={formItem === "new" ? undefined : formItem}
          adminSecret={adminSecret}
          onSaved={() => void handleFormSaved()}
          onCancel={() => setFormItem(null)}
        />
      )}
    </main>
  );
}
