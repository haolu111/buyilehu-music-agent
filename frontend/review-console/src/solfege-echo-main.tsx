import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { SolfegeEchoActivity } from "./activity/SolfegeEchoActivity";
import { useRuntimeMusicContent } from "./shared/useRuntimeMusicContent";

function RuntimeSolfegeEcho() {
  const runtime = useRuntimeMusicContent();
  return <SolfegeEchoActivity key={runtime.revisionKey} state={{ config: runtime.config }} />;
}

ReactDOM.createRoot(document.getElementById("solfege-echo-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <RuntimeSolfegeEcho />
    </Theme>
  </React.StrictMode>
);
