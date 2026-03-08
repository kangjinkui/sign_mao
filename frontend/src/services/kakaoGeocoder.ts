import type { GeocodeCandidate } from "../types/radius";
import { loadKakaoMaps } from "./kakaoMapLoader";

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

function extractRoadAddress(address: string): string | null {
  const compact = address.replace(/\s+/g, " ").trim();
  const match = compact.match(
    /(서울특별시|서울시)\s+강남구\s+([^\d]+?(?:대로|로|길))\s*(\d+(?:-\d+)?)/u
  );
  if (!match) return null;
  const city = match[1] === "서울시" ? "서울특별시" : match[1];
  const road = match[2].trim();
  const no = match[3].trim();
  return `${city} 강남구 ${road} ${no}`;
}

function buildFallbackQueries(address: string): string[] {
  const base = address.trim();
  const variants = new Set<string>([base]);
  const noParen = base.replace(/\([^)]*\)/g, " ").replace(/\s+/g, " ").trim();
  variants.add(noParen);
  variants.add(noParen.replace(/지상\s*\d+층/g, " ").replace(/\s+/g, " ").trim());
  variants.add(noParen.replace(/\s+옥상층/g, " ").replace(/\s+/g, " ").trim());
  const roadOnly = extractRoadAddress(noParen);
  if (roadOnly) variants.add(roadOnly);
  return Array.from(variants).filter((item) => item.length > 0);
}

export async function geocodeAddress(address: string): Promise<GeocodeCandidate[]> {
  const kakao = await loadKakaoMaps();
  const geocoder = new kakao.maps.services.Geocoder();

  for (const query of buildFallbackQueries(address)) {
    for (let attempt = 0; attempt < 3; attempt += 1) {
      const candidates = await new Promise<GeocodeCandidate[]>((resolve) => {
        geocoder.addressSearch(query, (result, status) => {
          if (status !== kakao.maps.services.Status.OK) {
            resolve([]);
            return;
          }
          resolve(
            result.map((item, index) => ({
              candidate_id: `kakao-js-${index}`,
              address: item.address_name,
              lat: Number(item.y),
              lng: Number(item.x),
            }))
          );
        });
      });
      if (candidates.length > 0) {
        return candidates;
      }
      await sleep(120);
    }
  }
  return [];
}
