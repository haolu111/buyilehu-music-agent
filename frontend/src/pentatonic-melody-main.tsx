import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { PentatonicMelodyActivity } from "./activity/PentatonicMelodyActivity";

ReactDOM.createRoot(document.getElementById("pentatonic-melody-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <PentatonicMelodyActivity />
    </Theme>
  </React.StrictMode>
);
