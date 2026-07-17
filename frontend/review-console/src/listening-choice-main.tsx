import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { ListeningChoiceActivity } from "./activity/ListeningChoiceActivity";
import { useRuntimeMusicContent } from "./shared/useRuntimeMusicContent";

function RuntimeListeningChoice() {
  const runtime = useRuntimeMusicContent();
  return <ListeningChoiceActivity key={runtime.revisionKey} state={{ config: runtime.config }} />;
}

ReactDOM.createRoot(document.getElementById("listening-choice-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <RuntimeListeningChoice />
    </Theme>
  </React.StrictMode>
);
