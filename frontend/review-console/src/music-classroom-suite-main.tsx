import React from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { MusicClassroomSuiteApp } from "./activity/MusicClassroomSuiteApp";

ReactDOM.createRoot(document.getElementById("music-classroom-suite-root") as HTMLElement).render(
  <React.StrictMode><Theme accentColor="teal" grayColor="sage" radius="large" scaling="100%"><MusicClassroomSuiteApp /></Theme></React.StrictMode>
);
