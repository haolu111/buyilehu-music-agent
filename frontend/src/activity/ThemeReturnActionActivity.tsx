import { Badge, Button, Container, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import { CheckCircle2, Ear, Play, RotateCcw, Volume2 } from "lucide-react";
import { useMemo, useState } from "react";
import { playPlayableInstrumentSequence } from "../shared/realAudio";
import {
  buildThemeReturnPlan,
  buildThemeReturnRecordExport,
  buildThemeReturnSummary,
  judgeThemeReturnAction,
  recordThemeReturnAttempt,
  type ThemeReturnAttempt
} from "./themeReturnActionLogic";
import "./primaryActivity.css";

type ThemeReturnActionState = {
  workflow?: {
    education_alignment?: {
      primary_competency?: string;
      music_elements?: string[];
      student_practices?: string[];
    };
  };
  config?: {
    theme_label?: string;
    theme_windows?: { startSec: number; endSec: number; label: string }[];
    action_choices?: string[];
    correct_action?: string;
    evidence_terms?: string[];
    audio_clip?: string;
    replay_required?: boolean;
  };
};

declare global {
  interface Window {
    __THEME_RETURN_ACTION_STATE__?: ThemeReturnActionState;
  }
}

const defaultState: ThemeReturnActionState = {
  workflow: {
    education_alignment: {
      primary_competency: "审美感知",
      music_elements: ["主题", "重复", "再现"],
      student_practices: ["listen", "move", "explain"]
    }
  },
  config: {
    theme_label: "A 主题",
    theme_windows: [
      { startSec: 8, endSec: 14, label: "第一次出现" },
      { startSec: 32, endSec: 40, label: "主题再现" },
    ],
    action_choices: ["举主题卡", "画圆", "拍肩"],
    correct_action: "举主题卡",
    evidence_terms: ["旋律相同", "节奏相似", "力度变化"],
    replay_required: true
  }
};

export function ThemeReturnActionActivity({ state = window.__THEME_RETURN_ACTION_STATE__ ?? defaultState }: { state?: ThemeReturnActionState }) {
  const config = state.config ?? defaultState.config ?? {};
  const alignment = state.workflow?.education_alignment ?? defaultState.workflow?.education_alignment ?? {};
  const plan = useMemo(() => buildThemeReturnPlan({
    themeLabel: config.theme_label,
    themeWindows: config.theme_windows,
    actionChoices: config.action_choices,
    correctAction: config.correct_action,
    evidenceTerms: config.evidence_terms,
    replayRequired: config.replay_required,
  }), [config.action_choices, config.correct_action, config.evidence_terms, config.replay_required, config.theme_label, config.theme_windows]);

  const [heardTheme, setHeardTheme] = useState(false);
  const [timestampSec, setTimestampSec] = useState(plan.themeWindows[0]?.startSec ?? 0);
  const [selectedAction, setSelectedAction] = useState("");
  const [selectedEvidence, setSelectedEvidence] = useState<string[]>([]);
  const [attempts, setAttempts] = useState<ThemeReturnAttempt[]>([]);
  const [submitted, setSubmitted] = useState(false);
  const judgement = judgeThemeReturnAction(plan, timestampSec, selectedAction, selectedEvidence, heardTheme);
  const summary = useMemo(() => buildThemeReturnSummary(plan, attempts), [attempts, plan]);
  const recordExport = useMemo(() => buildThemeReturnRecordExport(summary), [summary]);

  const playTheme = () => {
    setHeardTheme(true);
    setSubmitted(false);
    setTimestampSec(plan.themeWindows[0]?.startSec ?? 8);
    playThemeCue();
  };

  const relistenReturn = () => {
    setHeardTheme(true);
    setSubmitted(false);
    setTimestampSec((plan.themeWindows[1] ?? plan.themeWindows[0])?.startSec + 1);
    playThemeCue();
  };

  const toggleEvidence = (term: string) => {
    setSubmitted(false);
    setSelectedEvidence((current) =>
      current.includes(term) ? current.filter((item) => item !== term) : [...current, term]
    );
  };

  const submitAttempt = () => {
    setAttempts((current) => recordThemeReturnAttempt(current, {
      action: selectedAction,
      evidenceTerms: selectedEvidence,
      heardTheme,
      timestampSec,
    }, plan));
    setSubmitted(true);
  };

  const reset = () => {
    setHeardTheme(false);
    setTimestampSec(plan.themeWindows[0]?.startSec ?? 0);
    setSelectedAction("");
    setSelectedEvidence([]);
    setAttempts([]);
    setSubmitted(false);
  };

  return (
    <main className="primary-activity-shell theme-return-shell">
      <Container size="4" px="4">
        <section className="teacher-control-bar">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2" wrap="wrap">
              <Ear size={18} />
              <Text weight="bold">主题再现动作控制</Text>
              <Badge color={heardTheme ? "green" : "amber"} variant="soft">{heardTheme ? "已听主题" : "先听主题"}</Badge>
              <Badge color="teal" variant="soft">{Math.round(timestampSec)} 秒</Badge>
            </Flex>
            <Flex gap="2" wrap="wrap">
              <Button highContrast onClick={playTheme} aria-label="播放主题">
                <Volume2 size={17} />
                播放主题
              </Button>
              <Button variant="soft" onClick={relistenReturn} aria-label="复听主题再现">
                <Play size={17} />
                复听主题再现
              </Button>
              <Button variant="soft" color="gray" onClick={reset} aria-label="重置">
                <RotateCcw size={17} />
              </Button>
            </Flex>
          </Flex>
        </section>

        <Grid columns={{ initial: "1", md: "1.08fr .92fr" }} gap="4" className="activity-stage">
          <section className="activity-board theme-return-board" aria-label="主题再现动作活动">
            <Flex align="center" gap="2" wrap="wrap">
              <Badge color="teal" variant="soft">{alignment.primary_competency ?? "审美感知"}</Badge>
              {(alignment.music_elements ?? []).map((element) => <Badge key={element} color="amber" variant="soft">{element}</Badge>)}
            </Flex>
            <Heading as="h1" size="8" className="activity-title">主题再现动作</Heading>
            <Text as="p" size="3" color="gray" className="activity-subtitle">
              先听清 {plan.themeLabel}，复听时在主题回来的一刻做约定动作，并说出旋律或节奏依据。
            </Text>

            <Text weight="bold" className="tool-label">主题时间窗</Text>
            <div className="theme-window-track" aria-label="主题时间窗">
              {plan.themeWindows.map((window) => (
                <button
                  key={window.id}
                  type="button"
                  className={timestampSec >= window.startSec && timestampSec <= window.endSec ? "active" : ""}
                  onClick={() => {
                    setTimestampSec(window.startSec + 1);
                    setSubmitted(false);
                  }}
                >
                  <strong>{window.label}</strong>
                  <span>{window.startSec}s - {window.endSec}s</span>
                </button>
              ))}
            </div>

            <Text weight="bold" className="tool-label">主题动作卡</Text>
            <div className="theme-action-grid" aria-label="主题动作卡">
              {plan.actionChoices.map((action) => (
                <button
                  key={action}
                  type="button"
                  className={selectedAction === action ? "active" : ""}
                  onClick={() => {
                    setSelectedAction(action);
                    setSubmitted(false);
                  }}
                >
                  {action}
                </button>
              ))}
            </div>
          </section>

          <aside className="activity-side" aria-label="主题再现记录区">
            <section className={`primary-tool theme-return-feedback ${judgement.status}`}>
              <Text weight="bold">音乐判断</Text>
              <p>{judgement.feedback}</p>
              <p>不是听到“好听”就做动作，而是听到主题旋律、节奏或力度特征回来。</p>
            </section>

            <section className="primary-tool evidence-panel">
              <Text weight="bold">选择音乐依据</Text>
              <div className="evidence-chip-grid">
                {plan.evidenceTerms.map((term) => (
                  <button
                    key={term}
                    type="button"
                    className={selectedEvidence.includes(term) ? "active" : ""}
                    onClick={() => toggleEvidence(term)}
                  >
                    {term}
                  </button>
                ))}
              </div>
              <Button size="4" highContrast onClick={submitAttempt} disabled={!selectedAction}>
                <CheckCircle2 size={18} />
                记录本次反应
              </Button>
              {submitted ? <Text size="2" color="green">主题再现记录已保存。</Text> : null}
            </section>

            <section className="primary-tool theme-return-record-panel">
              <Text weight="bold">主题再现记录</Text>
              <div className="theme-return-stats">
                <span>尝试：{summary.attemptCount} 次</span>
                <span>准确：{summary.correctCount} 次</span>
                <span>依据：{summary.evidenceTerms.join("、") || "待选择"}</span>
                <span>{summary.readyForClassShare ? "可全班分享" : "继续复听"}</span>
              </div>
              <p>{summary.teacherNextStep}</p>
              <pre aria-label="主题再现记录导出 JSON">{recordExport}</pre>
            </section>
          </aside>
        </Grid>
      </Container>
    </main>
  );
}

function playThemeCue() {
  playPlayableInstrumentSequence([0, 2, 4, 2, 0], {
    instrument: "simple_keyboard",
    gap: 0.28,
    duration: 0.24,
    gain: 0.56,
    baseMidi: 60,
    oscillatorWave: "sine"
  });
}
