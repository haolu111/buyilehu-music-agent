import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { BodyPercussionActivity } from "./activity/BodyPercussionActivity";

ReactDOM.createRoot(document.getElementById("body-percussion-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <BodyPercussionActivity />
    </Theme>
  </React.StrictMode>
);
