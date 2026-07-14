import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { PrimaryActivityLibraryApp } from "./activity/PrimaryActivityLibraryApp";

ReactDOM.createRoot(document.getElementById("primary-library-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <PrimaryActivityLibraryApp />
    </Theme>
  </React.StrictMode>
);
