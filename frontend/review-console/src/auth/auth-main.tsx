import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import "./AuthApp.css";
import { AuthApp } from "./AuthApp";

ReactDOM.createRoot(document.getElementById("auth-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <AuthApp />
    </Theme>
  </React.StrictMode>
);
