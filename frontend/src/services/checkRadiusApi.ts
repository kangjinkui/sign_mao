import type { RadiusResponse } from "../types/radius";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:18100";

type CheckParams = {
  address: string;
  selected_candidate_id?: string;
  lat?: number;
  lng?: number;
  legal_dong?: string;
  ad_type?: string;
};

export async function checkRadius(params: CheckParams): Promise<RadiusResponse> {
  const response = await fetch(`${BASE_URL}/api/v1/check-radius`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params)
  });

  const payload = await response.json();
  if (!response.ok) {
    const message = payload?.message ?? "요청 실패";
    const error = new Error(message) as Error & { details?: unknown; code?: string; status?: number };
    error.details = payload?.details;
    error.code = payload?.code;
    error.status = response.status;
    throw error;
  }

  return payload as RadiusResponse;
}

export function mapRadiusItemsForList(items: RadiusResponse["items"]): string[] {
  return items.map((item) => `${item.company} (${Math.round(item.distance_m)}m)`);
}
