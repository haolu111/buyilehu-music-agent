import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { SteadyBeatWalkActivity } from "./activity/SteadyBeatWalkActivity";
import { useRuntimeMusicContent } from "./shared/useRuntimeMusicContent";

function RuntimeSteadyBeatWalk() {
  const runtime = useRuntimeMusicContent();
  return <SteadyBeatWalkActivity key={runtime.revisionKey} state={{ config: runtime.config }} />;
}

ReactDOM.createRoot(document.getElementById("steady-beat-walk-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <RuntimeSteadyBeatWalk />
    </Theme>
  </React.StrictMode>
);
