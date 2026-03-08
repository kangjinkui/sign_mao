import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { RadiusCheckPage } from "../../src/pages/RadiusCheckPage";

describe("RadiusCheckPage", () => {
  it("검색 후 결과 목록을 표시한다", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: true,
        json: async () => ({
          input: { address: "서울 강남구 도산대로 306", lat: 37.52, lng: 127.02 },
          radius: 200,
          count: 1,
          items: [
            { company: "ABC", ad_type: "ROOFTOP_LED", address: "서울 강남구", distance_m: 85 }
          ],
          geocode_candidates: []
        })
      }))
    );

    render(<RadiusCheckPage />);
    fireEvent.change(screen.getByLabelText("address-input"), {
      target: { value: "서울 강남구 도산대로 306" }
    });
    fireEvent.click(screen.getByRole("button", { name: "검색" }));

    await waitFor(() => {
      expect(screen.getByText(/검색 결과 \(1\)/)).toBeInTheDocument();
      expect(screen.getByText(/ABC/)).toBeInTheDocument();
    });
  });
});
