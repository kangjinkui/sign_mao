import { describe, expect, it } from "vitest";

import { mapRadiusItemsForList } from "../../src/services/checkRadiusApi";

describe("mapRadiusItemsForList", () => {
  it("거리 포함 텍스트로 변환한다", () => {
    const mapped = mapRadiusItemsForList([
      { company: "A", ad_type: "ROOFTOP_LED", address: "x", distance_m: 85.2 }
    ]);
    expect(mapped[0]).toContain("A");
    expect(mapped[0]).toContain("85m");
  });
});
