import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { MusicEducationReviewApp } from "./activity/MusicEducationReviewApp";
import "./activity/primaryActivity.css";

ReactDOM.createRoot(document.getElementById("music-education-review-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <MusicEducationReviewApp />
    </Theme>
  </React.StrictMode>
);
