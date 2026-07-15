import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { ExitTicketActivity } from "./activity/ExitTicketActivity";

ReactDOM.createRoot(document.getElementById("exit-ticket-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <ExitTicketActivity />
    </Theme>
  </React.StrictMode>
);
