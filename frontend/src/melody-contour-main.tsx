import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { MelodyContourTraceActivity } from "./activity/MelodyContourTraceActivity";

ReactDOM.createRoot(document.getElementById("melody-contour-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <MelodyContourTraceActivity />
    </Theme>
  </React.StrictMode>
);
