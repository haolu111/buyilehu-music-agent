import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { GraphicScoreActivity } from "./activity/GraphicScoreActivity";

ReactDOM.createRoot(document.getElementById("graphic-score-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <GraphicScoreActivity />
    </Theme>
  </React.StrictMode>
);
