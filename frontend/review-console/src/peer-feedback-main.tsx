import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { PeerFeedbackActivity } from "./activity/PeerFeedbackActivity";

ReactDOM.createRoot(document.getElementById("peer-feedback-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <PeerFeedbackActivity />
    </Theme>
  </React.StrictMode>
);
