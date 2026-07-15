import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { SimpleScoreFollowingActivity } from "./activity/SimpleScoreFollowingActivity";

ReactDOM.createRoot(document.getElementById("simple-score-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <SimpleScoreFollowingActivity />
    </Theme>
  </React.StrictMode>
);
