import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { RhythmQuestionAnswerActivity } from "./activity/RhythmQuestionAnswerActivity";

ReactDOM.createRoot(document.getElementById("rhythm-question-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <RhythmQuestionAnswerActivity />
    </Theme>
  </React.StrictMode>
);
