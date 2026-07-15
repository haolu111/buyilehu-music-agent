import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { PhraseSingingActivity } from "./activity/PhraseSingingActivity";

ReactDOM.createRoot(document.getElementById("phrase-singing-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <PhraseSingingActivity />
    </Theme>
  </React.StrictMode>
);
