import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./tests",
  fullyParallel: false,
  workers: 1,
  timeout: 30000,
  use: { baseURL: "http://localhost:4173", headless: true, channel: "chrome" },
  reporter: "list",
});
