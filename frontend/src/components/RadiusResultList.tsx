import type { RadiusItem } from "../types/radius";
import { formatAdType } from "../utils/adTypeLabel";

type Props = {
  items: RadiusItem[];
  onMoveToMap: (item: RadiusItem) => void;
  adminMode?: boolean;
  onEdit?: (item: RadiusItem) => void;
  onDelete?: (item: RadiusItem) => void;
};

export function RadiusResultList({ items, onMoveToMap, adminMode, onEdit, onDelete }: Props) {
  return (
    <section aria-label="result-list">
      <h2>검색 결과 ({items.length})</h2>
      <ul>
        {items.map((item, index) => (
          <li key={`${item.id}-${index}`} style={{ marginBottom: 8 }}>
            <div>
              <strong>{item.company}</strong>
            </div>
            <div>광고물 종류: {formatAdType(item.ad_type)}</div>
            <div>표시주소: {item.address}</div>
            <div style={{ display: "flex", gap: 4, marginTop: 4 }}>
              <button onClick={() => onMoveToMap(item)}>지도에서 보기</button>
              {adminMode && (
                <>
                  <button onClick={() => onEdit?.(item)}>수정</button>
                  <button onClick={() => onDelete?.(item)} style={{ color: "red" }}>삭제</button>
                </>
              )}
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
