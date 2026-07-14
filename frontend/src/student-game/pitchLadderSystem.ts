export type PitchDirection = "higher" | "same" | "lower";

export type PitchSystemStatus = "ready" | "listening" | "playing" | "round_clear" | "mission_success" | "mission_failed";

export type PitchSystemJudgement = "correct" | "wrong" | "partial" | "sing_back";

export type PitchSystemRound = {
  sequence?: string[];
  labels?: string[];
  answer?: string | string[];
};

export type PitchSystemState = {
  status: PitchSystemStatus;
  currentRound: number;
  actorLane: PitchDirection;
  cleared: number;
  mistakes: number;
  energy: number;
  selected: string[];
  message: string;
  lastJudgement?: PitchSystemJudgement;
  pendingMissionDone?: boolean;
};

export type PitchSystemConfig = {
  rounds: PitchSystemRound[];
  energyMax: number;
  mistakeLimit: number;
};

export type PitchSystemOutcome = {
  type:
    | "listen"
    | "playing"
    | "preview"
    | "voice_start"
    | "voice_retry"
    | "success"
    | "partial"
    | "mistake"
    | "mission_failed"
    | "round_clear"
    | "mission_success"
    | "reset";
  message: string;
  judgement?: PitchSystemJudgement;
  selection?: string[];
  direction?: PitchDirection;
  missionDone?: boolean;
};

export function createPitchSystemState(config: PitchSystemConfig): PitchSystemState {
  return {
    status: "ready",
    currentRound: 0,
    actorLane: "lower",
    cleared: 0,
    mistakes: 0,
    energy: config.energyMax,
    selected: [],
    message: "听音",
    lastJudgement: undefined,
    pendingMissionDone: false
  };
}

export function isPitchDirection(value: string | undefined): value is PitchDirection {
  return value === "higher" || value === "same" || value === "lower";
}

export class PitchLadderGameSystem {
  readonly config: PitchSystemConfig;
  state: PitchSystemState;

  constructor(config: PitchSystemConfig) {
    this.config = {
      ...config,
      rounds: config.rounds.length ? config.rounds : [{ sequence: ["do", "re"], answer: "higher" }],
      energyMax: Math.max(1, config.energyMax),
      mistakeLimit: Math.max(1, config.mistakeLimit)
    };
    this.state = createPitchSystemState(this.config);
  }

  reset(): PitchSystemOutcome {
    this.state = createPitchSystemState(this.config);
    return { type: "reset", message: "听音" };
  }

  listen(): PitchSystemOutcome {
    if (this.isFinished()) return { type: this.state.status === "mission_success" ? "mission_success" : "mission_failed", message: this.state.message };
    this.state.status = "listening";
    this.state.message = "听音";
    this.state.lastJudgement = undefined;
    return { type: "listen", message: "听音" };
  }

  enterPlaying(message = "选"): PitchSystemOutcome {
    if (this.state.status !== "listening") return { type: "playing", message: this.state.message };
    this.state.status = "playing";
    this.state.message = message;
    return { type: "playing", message };
  }

  previewDirection(direction: string): PitchSystemOutcome {
    if (this.isFinished() || this.state.status === "round_clear" || !isPitchDirection(direction)) return { type: "preview", message: this.state.message };
    this.state.status = "playing";
    this.state.selected = [direction];
    this.state.message = `唱${pitchDirectionLabel(direction)}`;
    this.state.lastJudgement = undefined;
    return { type: "preview", message: this.state.message, direction };
  }

  startVoiceCharge(): PitchSystemOutcome {
    if (this.isFinished() || this.state.status === "round_clear") return { type: "voice_start", message: this.state.message };
    this.state.status = "playing";
    this.state.message = "唱回";
    return { type: "voice_start", message: this.state.message };
  }

  voiceRetry(message: string): PitchSystemOutcome {
    if (this.isFinished()) return { type: "voice_retry", message: this.state.message };
    this.state.message = message || "再唱一次";
    return { type: "voice_retry", message: this.state.message };
  }

  chooseDirection(direction: string): PitchSystemOutcome {
    if (this.isFinished() || this.state.status === "round_clear" || !isPitchDirection(direction)) return { type: "playing", message: this.state.message };
    const expected = this.expectedDirection();
    if (direction === expected) return this.markRoundClear([direction], direction, "平台对了", "correct");
    return this.registerMistake(directionMistakeMessage(direction, expected));
  }

  resolveVoiceAttempt(choice: string, voiceDirection: string): PitchSystemOutcome {
    if (this.isFinished() || !isPitchDirection(choice) || !isPitchDirection(voiceDirection)) {
      return { type: "playing", message: this.state.message };
    }
    if (this.state.status === "round_clear") return { type: "playing", message: this.state.message };
    const expected = this.expectedDirection();
    if (choice === expected && voiceDirection === expected) return this.markRoundClear([choice], choice, "听准唱稳", "correct");
    if (choice === expected) return this.registerMistake("听对了，唱的方向不稳");
    if (voiceDirection === expected) return this.registerMistake("声音方向对了，再听清目标音");
    return this.registerMistake("高低都要再听");
  }

  chooseNode(note: string): PitchSystemOutcome {
    if (this.isFinished() || this.state.status === "round_clear") return { type: "playing", message: this.state.message };
    const answer = this.currentAnswerList();
    const next = [...this.state.selected, note].slice(0, answer.length);
    const expected = answer[this.state.selected.length] || answer[0];
    if (note !== expected) return this.registerMistake("滑落");
    this.state.selected = next;
    if (next.length < answer.length) {
      this.state.message = "继续";
      this.state.lastJudgement = "partial";
      return { type: "partial", message: "继续", judgement: "partial", selection: next };
    }
    return this.markRoundClear(next, undefined, "拿宝石", "correct");
  }

  confirmSingBack(): PitchSystemOutcome {
    if (this.state.status !== "round_clear") return { type: "playing", message: this.state.message };
    if (this.state.pendingMissionDone) {
      this.state.status = "mission_success";
      this.state.message = "登顶";
      this.state.lastJudgement = "sing_back";
      return {
        type: "mission_success",
        message: this.state.message,
        judgement: "sing_back",
        selection: [...this.state.selected],
        missionDone: true
      };
    }
    return this.advanceRound();
  }

  advanceRound(): PitchSystemOutcome {
    if (this.state.status !== "round_clear") return { type: "playing", message: this.state.message };
    this.state.currentRound += 1;
    this.state.selected = [];
    this.state.status = "ready";
    this.state.message = "听音";
    this.state.lastJudgement = undefined;
    this.state.pendingMissionDone = false;
    return { type: "playing", message: "下一关" };
  }

  expectedDirection(): PitchDirection {
    const answer = String(this.currentRound().answer || "higher");
    return isPitchDirection(answer) ? answer : "higher";
  }

  currentRound(): PitchSystemRound {
    return this.config.rounds[this.state.currentRound % this.config.rounds.length];
  }

  currentSequence(): string[] {
    return (this.currentRound().sequence || []).map(String);
  }

  private markRoundClear(selection: string[], direction: PitchDirection | undefined, message: string, judgement: PitchSystemJudgement): PitchSystemOutcome {
    const missionDone = this.state.currentRound + 1 >= this.config.rounds.length;
    this.state.status = direction && missionDone ? "mission_success" : "round_clear";
    this.state.selected = selection;
    this.state.cleared = Math.max(this.state.cleared, this.state.currentRound + 1);
    this.state.message = direction && missionDone ? "登顶" : message;
    this.state.lastJudgement = judgement;
    this.state.pendingMissionDone = missionDone && !direction;
    if (direction) this.state.actorLane = direction;
    return {
      type: direction && missionDone ? "mission_success" : "round_clear",
      message: this.state.message,
      judgement,
      selection,
      direction,
      missionDone
    };
  }

  private registerMistake(message: string): PitchSystemOutcome {
    this.state.mistakes += 1;
    this.state.energy = Math.max(0, this.state.energy - Math.ceil(this.config.energyMax / this.config.mistakeLimit));
    const failed = this.state.energy <= 0 || this.state.mistakes >= this.config.mistakeLimit;
    this.state.status = failed ? "mission_failed" : "playing";
    this.state.message = message;
    this.state.lastJudgement = "wrong";
    return { type: failed ? "mission_failed" : "mistake", message: failed ? "再听" : message, judgement: "wrong" };
  }

  private currentAnswerList(): string[] {
    const answer = this.currentRound().answer;
    return Array.isArray(answer) ? answer.map(String) : [String(answer || "")];
  }

  private isFinished() {
    return this.state.status === "mission_success" || this.state.status === "mission_failed";
  }
}

export function pitchDirectionLabel(direction: PitchDirection) {
  return {
    higher: "更高",
    same: "一样高",
    lower: "更低"
  }[direction];
}

function directionMistakeMessage(choice: PitchDirection, expected: PitchDirection) {
  if (choice === "higher") return expected === "lower" ? "跳高了" : "不是更高";
  if (choice === "lower") return expected === "higher" ? "滑低了" : "不是更低";
  return expected === "higher" ? "要更高" : "要更低";
}
