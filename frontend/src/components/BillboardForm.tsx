import { useState } from "react";
import type { RadiusItem } from "../types/radius";
import { createBillboard, updateBillboard } from "../services/billboardsApi";
import { geocodeAddress } from "../services/kakaoGeocoder";

const AD_TYPE_OPTIONS = [
  { value: "ROOFTOP_LED", label: "옥상전광" },
  { value: "WALL_LED", label: "벽면전광" },
];

type Props = {
  item?: RadiusItem;
  adminSecret: string;
  onSaved: () => void;
  onCancel: () => void;
};

export function BillboardForm({ item, adminSecret, onSaved, onCancel }: Props) {
  const isEdit = item !== undefined;
  const [companyName, setCompanyName] = useState(item?.company ?? "");
  const [adType, setAdType] = useState(item?.ad_type ?? "ROOFTOP_LED");
  const [address, setAddress] = useState(item?.address ?? "");
  const [permitDate, setPermitDate] = useState(item?.permit_date ?? "");
  const [sizeText, setSizeText] = useState(item?.size_text ?? "");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!companyName.trim() || !address.trim()) {
      setError("업체명과 표시주소는 필수입니다.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      let lat: number | undefined;
      let lng: number | undefined;
      const candidates = await geocodeAddress(address);
      if (candidates.length > 0) {
        lat = candidates[0].lat;
        lng = candidates[0].lng;
      }

      const payload = {
        company_name: companyName.trim(),
        ad_type: adType,
        display_address: address.trim(),
        permit_date: permitDate || undefined,
        size_text: sizeText || undefined,
        lat,
        lng,
      };

      if (isEdit && item) {
        await updateBillboard(item.id, payload, adminSecret);
      } else {
        await createBillboard(payload, adminSecret);
      }
      onSaved();
    } catch (err) {
      setError(err instanceof Error ? err.message : "저장 중 오류가 발생했습니다.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,0.4)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
      }}
    >
      <form
        onSubmit={(e) => void handleSubmit(e)}
        style={{
          background: "#fff",
          padding: 24,
          borderRadius: 8,
          width: 360,
          display: "grid",
          gap: 12,
        }}
      >
        <h3 style={{ margin: 0 }}>{isEdit ? "광고물 수정" : "광고물 등록"}</h3>

        <label style={{ display: "grid", gap: 4 }}>
          <span>업체명 *</span>
          <input value={companyName} onChange={(e) => setCompanyName(e.target.value)} />
        </label>

        <label style={{ display: "grid", gap: 4 }}>
          <span>광고물 종류 *</span>
          <select value={adType} onChange={(e) => setAdType(e.target.value)}>
            {AD_TYPE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </label>

        <label style={{ display: "grid", gap: 4 }}>
          <span>표시주소 *</span>
          <input value={address} onChange={(e) => setAddress(e.target.value)} />
        </label>

        <label style={{ display: "grid", gap: 4 }}>
          <span>허가일</span>
          <input type="date" value={permitDate ?? ""} onChange={(e) => setPermitDate(e.target.value)} />
        </label>

        <label style={{ display: "grid", gap: 4 }}>
          <span>크기</span>
          <input placeholder="예: 5.0m x 3.0m" value={sizeText ?? ""} onChange={(e) => setSizeText(e.target.value)} />
        </label>

        {error && <p style={{ color: "red", margin: 0 }}>{error}</p>}

        <div style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
          <button type="button" onClick={onCancel}>취소</button>
          <button type="submit" disabled={saving}>{saving ? "저장 중..." : "저장"}</button>
        </div>
      </form>
    </div>
  );
}
