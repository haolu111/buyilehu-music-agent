import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { StrongWeakBeatActivity } from "./activity/StrongWeakBeatActivity";
import { useRuntimeMusicContent } from "./shared/useRuntimeMusicContent";

function RuntimeStrongWeakBeat() {
  const runtime = useRuntimeMusicContent();
  return <StrongWeakBeatActivity key={runtime.revisionKey} state={{ config: runtime.config as any }} />;
}

ReactDOM.createRoot(document.getElementById("strong-weak-beat-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <RuntimeStrongWeakBeat />
    </Theme>
  </React.StrictMode>
);
