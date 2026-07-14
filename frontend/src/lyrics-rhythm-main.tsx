import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { LyricsRhythmActivity } from "./activity/LyricsRhythmActivity";

ReactDOM.createRoot(document.getElementById("lyrics-rhythm-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <LyricsRhythmActivity />
    </Theme>
  </React.StrictMode>
);
