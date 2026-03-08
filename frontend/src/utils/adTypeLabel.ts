export function formatAdType(adType: string): string {
  if (adType === "ROOFTOP_LED") return "옥상전광";
  if (adType === "WALL_LED") return "벽면전광";
  return adType;
}
