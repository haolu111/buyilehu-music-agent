import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { GroupRelayActivity } from "./activity/GroupRelayActivity";

ReactDOM.createRoot(document.getElementById("group-relay-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <GroupRelayActivity />
    </Theme>
  </React.StrictMode>
);
