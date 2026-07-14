import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { InstrumentFamilySortingActivity } from "./activity/InstrumentFamilySortingActivity";

ReactDOM.createRoot(document.getElementById("instrument-family-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <InstrumentFamilySortingActivity />
    </Theme>
  </React.StrictMode>
);
