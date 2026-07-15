import { resolve } from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  base: "/template-console/",
  plugins: [vue(), react()],
  build: {
    manifest: true,
    rollupOptions: {
      input: {
        auth: resolve(__dirname, "auth.html"),
        index: resolve(__dirname, "index.html"),
        "student-game": resolve(__dirname, "student-game.html"),
        "beat-guardian-preview": resolve(__dirname, "beat-guardian-preview.html"),
        "lyrics-rhythm-preview": resolve(__dirname, "lyrics-rhythm-preview.html"),
        "lesson-opening-preview": resolve(__dirname, "lesson-opening-preview.html"),
        "steady-beat-walk-preview": resolve(__dirname, "steady-beat-walk-preview.html"),
        "listening-choice-preview": resolve(__dirname, "listening-choice-preview.html"),
        "theme-return-action-preview": resolve(__dirname, "theme-return-action-preview.html"),
        "graphic-score-preview": resolve(__dirname, "graphic-score-preview.html"),
        "strong-weak-beat-preview": resolve(__dirname, "strong-weak-beat-preview.html"),
        "instrument-family-preview": resolve(__dirname, "instrument-family-preview.html"),
        "melody-contour-preview": resolve(__dirname, "melody-contour-preview.html"),
        "body-percussion-preview": resolve(__dirname, "body-percussion-preview.html"),
        "group-relay-preview": resolve(__dirname, "group-relay-preview.html"),
        "peer-feedback-preview": resolve(__dirname, "peer-feedback-preview.html"),
        "exit-ticket-preview": resolve(__dirname, "exit-ticket-preview.html"),
        "orff-ensemble-preview": resolve(__dirname, "orff-ensemble-preview.html"),
        "phrase-singing-preview": resolve(__dirname, "phrase-singing-preview.html"),
        "solfege-echo-preview": resolve(__dirname, "solfege-echo-preview.html"),
        "simple-score-preview": resolve(__dirname, "simple-score-preview.html"),
        "pentatonic-melody-preview": resolve(__dirname, "pentatonic-melody-preview.html"),
        "music-education-review": resolve(__dirname, "music-education-review.html"),
        "music-classroom-suite": resolve(__dirname, "music-classroom-suite.html"),
        "virtual-instrument-review": resolve(__dirname, "virtual-instrument-review.html"),
        "primary-library": resolve(__dirname, "primary-library.html"),
        "primary-activity-preview": resolve(__dirname, "primary-activity-preview.html"),
        "rhythm-question-preview": resolve(__dirname, "rhythm-question-preview.html"),
        "teacher-activity": resolve(__dirname, "teacher-activity.html")
      }
    }
  },
  server: {
    port: 5176,
    proxy: {
      "/api": "http://127.0.0.1:8000",
      "/static": "http://127.0.0.1:8000",
      "/runtime-assets": "http://127.0.0.1:8000"
    }
  }
});
