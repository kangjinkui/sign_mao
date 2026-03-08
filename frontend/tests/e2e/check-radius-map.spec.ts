import { expect, test } from "@playwright/test";

test("주소 검색 -> 후보 선택 -> 지도 반영", async ({ page }) => {
  await page.goto("/");

  await page.getByLabel("address-input").fill("서울 강남구 도산대로");
  await page.getByRole("button", { name: "검색" }).click();

  await expect(page.getByText("지오코딩 후보 선택")).toBeVisible();
  await page.getByRole("button", { name: "서울 강남구 도산대로 306" }).click();

  await expect(page.getByRole("heading", { name: "검색 결과 (0)" })).toBeVisible();
  await expect(page.getByLabel("billboard-map")).toContainText("반경: 200m");
  await expect(page.getByLabel("billboard-map")).toContainText("중심: 37.5201, 127.0282");
});
