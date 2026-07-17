import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { RhythmQuestionAnswerActivity } from "./activity/RhythmQuestionAnswerActivity";
import { useRuntimeMusicContent } from "./shared/useRuntimeMusicContent";

function RuntimeRhythmQuestion() {
  const runtime = useRuntimeMusicContent();
  return <RhythmQuestionAnswerActivity key={runtime.revisionKey} state={{ config: runtime.config }} />;
}

ReactDOM.createRoot(document.getElementById("rhythm-question-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <RuntimeRhythmQuestion />
    </Theme>
  </React.StrictMode>
);
