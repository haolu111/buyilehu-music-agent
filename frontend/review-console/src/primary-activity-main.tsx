import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { RhythmWarmupActivity } from "./activity/RhythmWarmupActivity";
import "./activity/primaryActivity.css";

ReactDOM.createRoot(document.getElementById("primary-activity-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <RhythmWarmupActivity />
    </Theme>
  </React.StrictMode>
);
