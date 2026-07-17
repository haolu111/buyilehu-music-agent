import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom/client";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { StudentGameApp } from "./student-game/StudentGameApp";
import "./student-game/styles.css";
import type { StudentGameState } from "./student-game/types";
import { createStudentGameReviewState, resolveStudentGameReviewTemplate, type FormalGameTemplate } from "./student-game/studentGameReviewPreview";

declare global {
  interface Window {
    __STUDENT_GAME_STATE__?: StudentGameState;
  }
}

const root = document.getElementById("student-game-root");

if (root) {
  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <Theme accentColor="teal" grayColor="sage" radius="large" scaling="100%">
        <StudentGameRuntime />
      </Theme>
    </React.StrictMode>
  );
}

function StudentGameRuntime() {
  const reviewTemplateId = resolveStudentGameReviewTemplate(window.location.search);
  const isReview = new URLSearchParams(window.location.search).get("review") === "1";
  const providedState = window.__STUDENT_GAME_STATE__;
  const [state, setState] = useState<StudentGameState>(() => providedState ?? createStudentGameReviewState(reviewTemplateId));

  useEffect(() => {
    const receiveRuntimeConfig = (event: MessageEvent) => {
      if (event.origin !== window.location.origin) return;
      if (event.data?.type !== "buyilehu:load-music-content") return;
      const nextState = event.data?.config?.studentGameState;
      if (!nextState || typeof nextState !== "object") return;
      setState(nextState as StudentGameState);
    };
    window.addEventListener("message", receiveRuntimeConfig);
    window.parent?.postMessage({ type: "buyilehu:activity-ready" }, window.location.origin);
    return () => window.removeEventListener("message", receiveRuntimeConfig);
  }, []);

  useEffect(() => {
    if (!isReview || providedState) return;
    let cancelled = false;
    void fetch(`/api/game-templates/${encodeURIComponent(reviewTemplateId)}`)
      .then(async (response) => {
        if (!response.ok) throw new Error(`game template request failed: ${response.status}`);
        return response.json() as Promise<{ template?: FormalGameTemplate }>;
      })
      .then((payload) => {
        if (!cancelled && payload.template) {
          setState(createStudentGameReviewState(reviewTemplateId, payload.template));
        }
      })
      .catch(() => {
        // The review fixture stays available only while the formal template endpoint is unavailable.
      });
    return () => {
      cancelled = true;
    };
  }, [isReview, providedState, reviewTemplateId]);

  return <StudentGameApp state={state} />;
}

function createSolfegeTargetPreviewState(): StudentGameState {
  return {
    workflow: {
      workflow_kind: "direct_game",
      gameplay_blueprint: {
        student_facing_name: "唱名打靶",
        prompt: "听目标音，在心里唱一遍，再击中对应唱名靶。",
        scene_goal: "用听辨、内听和唱回完成唱名确认。",
        operation_type: "solfege_target",
        play_mode: "aim_and_sing",
        game_genre: "target_range"
      },
      experience_script: {
        opening_hook: "目标音出现后，先在心里唱出它，再瞄准。",
        progression: [
          { emotion: "听清目标", reward: "靶心亮起" },
          { emotion: "命中唱名", reward: "唱回徽章" }
        ],
        closure_prompt: "说出这个唱名在旋律里的位置感。"
      },
      theme_pack: {
        skin_family: "target_world",
        layout_variant: "target_arena",
        reward_token: "唱回徽章",
        scene: {
          setting: "唱名星靶场",
          objective_noun: "唱名靶",
          progress_noun: "命中",
          supporting_prop: "音符发射器"
        },
        play_mode: "aim_and_sing"
      },
      presentation_pack: {
        experience_variant_id: "solfege_target_direct_preview",
        play_mode: "aim_and_sing"
      }
    },
    instance: {
      template_label: "唱名打靶",
      student_task: {
        listen: "听什么：听目标音，在心里找到唱名。",
        do: "做什么：击中对应唱名靶，再唱回确认。",
        pass: "怎样过关：命中并完成唱回。"
      }
    },
    template_id: "solfege_target_core",
    age_ui_profile: "upper_primary",
    config: {
      template_id: "solfege_target_core",
      engine: "phaser_2d",
      scene_id: "solfege_target_scene",
      runtime_shell: "solfege_target_shell",
      game_genre: "target_range",
      camera_profile: "aiming_target_arena",
      hud_model: "reticle_hit_singback",
      interaction_model: "listen_aim_hit_sing",
      student_ui_mode: "game_first",
      mode: "aim_and_sing",
      current_mode: "aim_and_sing",
      skin_id: "star_target",
      skin_play_mode: "star",
      audio_mode: "hybrid",
      grade_band: "小学低段",
      music_concept: "唱名听辨与模唱",
      tonic: "C",
      solfege_system: "movable_do",
      scale_type: "major_pentatonic",
      target_solfege: ["do", "re", "mi", "sol", "la"],
      solfege_rounds: [
        { id: "preview-do", sequence: ["do"], labels: ["do"], answer: "do", midi_offsets: [0], sing_back_required: true, teacher_confirm_required: true },
        { id: "preview-mi", sequence: ["mi"], labels: ["mi"], answer: "mi", midi_offsets: [4], sing_back_required: true, teacher_confirm_required: true },
        { id: "preview-sol", sequence: ["sol"], labels: ["sol"], answer: "sol", midi_offsets: [7], sing_back_required: true, teacher_confirm_required: true }
      ],
      energy_max: 100,
      mistake_limit: 3,
      combo_milestones: [2, 4, 6],
      sing_back_required: true,
      teacher_confirm_required: true,
      mic_assist_enabled: true,
      show_solfege_hint: true,
      music_reason_prompts: {
        wrong_target: "唱名不对：先在心里唱出目标音。",
        right_target: "击中唱名：现在把它唱出来。",
        sing_back: "点击不是终点：请用自己的声音唱回。",
        success: "听辨和唱回完成：说出这个音的位置感。"
      },
      result_transfer_prompt: "说出这个唱名在旋律里的位置感。"
    },
    student_task_copy: {
      listen: "听什么：听目标音，在心里找到唱名。",
      do: "做什么：击中对应唱名靶，再唱回确认。",
      pass: "怎样过关：命中并完成唱回。"
    },
    music_reason_prompts: {
      wrong_target: "唱名不对：先在心里唱出目标音。",
      right_target: "击中唱名：现在把它唱出来。",
      sing_back: "点击不是终点：请用自己的声音唱回。",
      success: "听辨和唱回完成：说出这个音的位置感。"
    },
    result_transfer_prompt: "说出这个唱名在旋律里的位置感。"
  };
}
