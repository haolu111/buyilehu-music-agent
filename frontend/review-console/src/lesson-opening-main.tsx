import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { LessonOpeningActivity } from "./activity/LessonOpeningActivity";

ReactDOM.createRoot(document.getElementById("lesson-opening-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <LessonOpeningActivity />
    </Theme>
  </React.StrictMode>
);
