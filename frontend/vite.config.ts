import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "prompt",
      includeAssets: ["favicon.svg", "icons/*.png"],
      manifest: {
        id: "/",
        name: "Domina — Do erro ao domínio",
        short_name: "Domina",
        description: "Seu aprendizado, um passo de cada vez.",
        lang: "pt-BR",
        start_url: "/",
        scope: "/",
        display: "standalone",
        theme_color: "#141A2E",
        background_color: "#F5F3EC",
        icons: [
          { src: "/icons/icon-192.png", sizes: "192x192", type: "image/png" },
          { src: "/icons/icon-512.png", sizes: "512x512", type: "image/png" },
          {
            src: "/icons/maskable-512.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "maskable",
          },
        ],
      },
      workbox: {
        globPatterns: ["**/*.{js,css,html,png,svg,woff2}"],
        navigateFallback: "/index.html",
      },
    }),
  ],
  resolve: { alias: { "react-native": "react-native-web" } },
});
