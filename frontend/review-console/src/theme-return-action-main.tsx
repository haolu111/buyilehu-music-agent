import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { ThemeReturnActionActivity } from "./activity/ThemeReturnActionActivity";

ReactDOM.createRoot(document.getElementById("theme-return-action-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <ThemeReturnActionActivity />
    </Theme>
  </React.StrictMode>
);
