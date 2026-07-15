import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { OrffEnsembleActivity } from "./activity/OrffEnsembleActivity";

ReactDOM.createRoot(document.getElementById("orff-ensemble-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <OrffEnsembleActivity />
    </Theme>
  </React.StrictMode>
);
