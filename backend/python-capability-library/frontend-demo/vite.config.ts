import { resolve } from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [react(), vue()],
  build: {
    rollupOptions: {
      input: {
        "music-education-review": resolve(__dirname, "music-education-review.html"),
        "virtual-instrument-review": resolve(__dirname, "virtual-instrument-review.html"),
      },
    },
  },
  server: {
    host: "127.0.0.1",
    port: 5173,
  },
});
