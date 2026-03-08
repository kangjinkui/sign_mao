import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { viteSingleFile } from "vite-plugin-singlefile";

const isStandalone = process.env.VITE_STANDALONE === "true";

export default defineConfig({
  plugins: isStandalone ? [react(), viteSingleFile()] : [react()],
  build: isStandalone
    ? {
        assetsInlineLimit: 100_000_000,
        cssCodeSplit: false,
      }
    : {},
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
    exclude: ["tests/e2e/**", "node_modules/**"],
  },
});
