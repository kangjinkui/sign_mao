import type { RadiusItem } from "../types/radius";

const IS_STANDALONE = import.meta.env.VITE_STANDALONE === "true";
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:18100";

type BillboardListResponse = {
  count: number;
  items: Array<{
    id: number;
    company: string;
    ad_type: string;
    address: string;
    lat: number | null;
    lng: number | null;
    permit_date?: string | null;
    size_text?: string | null;
  }>;
};

export async function listBillboards(limit = 200): Promise<BillboardListResponse> {
  if (IS_STANDALONE) {
    const data = (await import("../data/billboards.json")) as BillboardListResponse;
    const items = data.items.slice(0, limit);
    return { count: items.length, items };
  }
  const response = await fetch(`${BASE_URL}/api/v1/billboards?limit=${limit}`);
  const payload = (await response.json()) as BillboardListResponse;
  if (!response.ok) {
    throw new Error("광고물 목록 조회 실패");
  }
  return payload;
}

export function toRadiusItem(item: BillboardListResponse["items"][number], lat: number, lng: number): RadiusItem {
  return {
    id: item.id,
    company: item.company,
    ad_type: item.ad_type,
    address: item.address,
    lat,
    lng,
    distance_m: 0,
    permit_date: item.permit_date,
    size_text: item.size_text,
  };
}

export type BillboardCreateInput = {
  company_name: string;
  ad_type: string;
  display_address: string;
  permit_date?: string;
  size_text?: string;
  lat?: number;
  lng?: number;
};

export async function createBillboard(data: BillboardCreateInput, secret: string): Promise<{ id: number }> {
  const response = await fetch(`${BASE_URL}/api/v1/billboards`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Admin-Secret": secret },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`등록 실패 (${response.status}): ${text}`);
  }
  return (await response.json()) as { id: number };
}

export type BillboardUpdateInput = Partial<BillboardCreateInput>;

export async function updateBillboard(id: number, data: BillboardUpdateInput, secret: string): Promise<void> {
  const response = await fetch(`${BASE_URL}/api/v1/billboards/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", "X-Admin-Secret": secret },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`수정 실패 (${response.status}): ${text}`);
  }
}

export async function deleteBillboard(id: number, secret: string): Promise<void> {
  const response = await fetch(`${BASE_URL}/api/v1/billboards/${id}`, {
    method: "DELETE",
    headers: { "X-Admin-Secret": secret },
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`삭제 실패 (${response.status}): ${text}`);
  }
}

export async function verifyAdminSecret(secret: string): Promise<boolean> {
  const response = await fetch(`${BASE_URL}/api/v1/auth/verify`, {
    method: "POST",
    headers: { "X-Admin-Secret": secret },
  });
  return response.ok;
}
