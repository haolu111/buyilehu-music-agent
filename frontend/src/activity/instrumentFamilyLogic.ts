import { playableInstrumentAssetFor } from "./playableInstrumentAssets";

export type InstrumentFamily = "吹奏" | "拉弦" | "弹拨" | "打击" | string;

export type InstrumentFamilyCard = {
  id: string;
  label: string;
  family: InstrumentFamily;
  evidence: string[];
  imageUrl?: string;
  visualSourceStatus: "generated_illustration" | "pending_generated_skin";
  audioSourceKind: "soundfont_fallback" | "webaudio_synthesis" | "open_sample";
  playbackInstrument: string;
  isRealSample: boolean;
  exactRealInstrumentSample: boolean;
  sampleFidelity: "exact_open_sample" | "close_soundfont_sample" | "approximate_soundfont_sample" | "not_real_sample";
  playableStatus: "ready_real_sample" | "ready_soundfont_proxy" | "pending_exact_sample";
  audioLicense: string;
  audioClassroomNote: string;
};

export type FamilySortResult = {
  status: "blocked_listen_first" | "needs_family" | "needs_evidence" | "correct" | "wrong_family";
  musicReason: string;
};

export function buildDefaultInstrumentCards(pool: string[], families: string[]): InstrumentFamilyCard[] {
  const normalizedFamilies = families.length ? families : ["吹奏", "拉弦", "弹拨", "打击"];
  return (pool.length ? pool : ["笛子", "二胡", "琵琶", "小鼓"]).map((label, index) => {
    const family = inferInstrumentFamily(label, normalizedFamilies, index);
    return {
      id: label.toLowerCase().replace(/\s+/g, "_"),
      label,
      family,
      evidence: evidenceForFamily(family),
      ...instrumentVisualSource(label),
      ...instrumentAudioSource(label),
    };
  });
}

export function judgeInstrumentFamilySort(input: {
  card: InstrumentFamilyCard;
  selectedFamily: string;
  selectedEvidence: string[];
  hasListened: boolean;
}): FamilySortResult {
  if (!input.hasListened) {
    return {
      status: "blocked_listen_first",
      musicReason: "乐器分类必须先听声音，图片和名称只能作为验证。",
    };
  }
  if (!input.selectedFamily) {
    return {
      status: "needs_family",
      musicReason: "请选择一个乐器家族或发声方式。",
    };
  }
  if (input.selectedFamily !== input.card.family) {
    return {
      status: "wrong_family",
      musicReason: `${input.card.label}更适合归入${input.card.family}，请回听它的发声方式。`,
    };
  }
  const hasEvidence = input.selectedEvidence.some((term) => input.card.evidence.includes(term));
  if (!hasEvidence) {
    return {
      status: "needs_evidence",
      musicReason: "分类正确，还需要补一个音色或发声方式依据。",
    };
  }
  return {
    status: "correct",
    musicReason: `${input.card.label}属于${input.card.family}，依据是${input.selectedEvidence.join("、")}。`,
  };
}

export function evidenceForFamily(family: string): string[] {
  if (family.includes("吹")) return ["气息感", "吹奏发声", "声音连贯"];
  if (family.includes("拉")) return ["弦鸣", "拉弦发声", "声音可连可断"];
  if (family.includes("弹")) return ["拨弦", "弹拨发声", "颗粒感"];
  if (family.includes("打")) return ["敲击感", "打击发声", "声音短促"];
  return ["音色特点", "发声方式", "作品语境"];
}

function inferInstrumentFamily(label: string, families: string[], index: number): string {
  const name = label.toLowerCase();
  const candidates: Array<[string[], string]> = [
    [["笛", "箫", "竖笛", "口风琴", "flute", "recorder", "melodica"], "吹奏"],
    [["二胡", "小提琴", "violin", "erhu"], "拉弦"],
    [["琵琶", "古筝", "吉他", "pipa", "guitar"], "弹拨"],
    [["鼓", "木鱼", "沙锤", "铃鼓", "三角铁", "hand_drum", "woodblock", "shaker", "triangle", "tambourine"], "打击"],
  ];
  for (const [keywords, family] of candidates) {
    if (keywords.some((keyword) => name.includes(keyword.toLowerCase())) && families.includes(family)) return family;
  }
  return families[index % families.length];
}

function instrumentVisualSource(label: string): Pick<InstrumentFamilyCard, "imageUrl" | "visualSourceStatus"> {
  const asset = playableInstrumentAssetFor(label);
  if (!asset.url) return { visualSourceStatus: "pending_generated_skin" };
  return { imageUrl: asset.url, visualSourceStatus: "generated_illustration" };
}

function instrumentAudioSource(
  label: string
): Pick<InstrumentFamilyCard, "audioSourceKind" | "playbackInstrument" | "isRealSample" | "exactRealInstrumentSample" | "sampleFidelity" | "playableStatus" | "audioLicense" | "audioClassroomNote"> {
  const name = label.toLowerCase();
  const sampleNote = "这是本地 SoundFont 采样音色，用于先听再分和虚拟乐器演奏；近似音色不得宣称为实体乐器精确录音。";
  const sources: Array<[string[], Pick<InstrumentFamilyCard, "audioSourceKind" | "playbackInstrument" | "isRealSample" | "exactRealInstrumentSample" | "sampleFidelity" | "playableStatus" | "audioLicense" | "audioClassroomNote">]> = [
    [["长笛", "flute_playable_board", "flute"], sampled("flute", "exact_open_sample", sampleNote)],
    [["笛子", "竹笛", "dizi", "dizi_playable_board"], sampled("flute", "approximate_soundfont_sample", `${sampleNote} 笛子当前用长笛 SoundFont 近似，待补笛子实录。`)],
    [["竖笛", "recorder"], sampled("flute", "approximate_soundfont_sample", `${sampleNote} 竖笛当前用长笛 SoundFont 近似，待补竖笛实录。`)],
    [["二胡", "erhu", "小提琴", "violin"], sampled("violin", "close_soundfont_sample", sampleNote)],
    [["琵琶", "pipa", "古筝", "guzheng"], sampled("koto", "close_soundfont_sample", sampleNote)],
    [["音条琴", "木琴", "xylophone"], sampled("xylophone", "exact_open_sample", sampleNote)],
    [["口风琴", "melodica"], sampled("acoustic_grand_piano", "approximate_soundfont_sample", `${sampleNote} 口风琴当前用钢琴 SoundFont 近似，待补口风琴实录。`)],
    [["小鼓", "鼓", "hand_drum", "drum"], sampled("taiko_drum", "close_soundfont_sample", `${sampleNote} 小鼓当前用鼓类 SoundFont 近似，待补小鼓实录。`)],
    [["木鱼", "woodblock", "响板", "claves"], sampled("woodblock", "close_soundfont_sample", sampleNote)],
    [["沙锤", "shaker", "maraca"], sampled("agogo", "approximate_soundfont_sample", `${sampleNote} 沙锤当前为近似采样。`)],
    [["三角铁", "triangle", "碰铃"], sampled("glockenspiel", "close_soundfont_sample", sampleNote)],
    [["铃鼓", "tambourine"], sampled("reverse_cymbal", "approximate_soundfont_sample", `${sampleNote} 铃鼓当前为近似采样。`)],
  ];
  const match = sources.find(([keywords]) => keywords.some((keyword) => name.includes(keyword.toLowerCase())));
  return match?.[1] ?? sampled("acoustic_grand_piano", "approximate_soundfont_sample", `${sampleNote} 当前乐器使用键盘近似音色，待补对应实录。`);
}

function sampled(
  playbackInstrument: string,
  sampleFidelity: InstrumentFamilyCard["sampleFidelity"],
  audioClassroomNote: string
): Pick<InstrumentFamilyCard, "audioSourceKind" | "playbackInstrument" | "isRealSample" | "exactRealInstrumentSample" | "sampleFidelity" | "playableStatus" | "audioLicense" | "audioClassroomNote"> {
  return {
    audioSourceKind: "open_sample",
    playbackInstrument,
    isRealSample: true,
    exactRealInstrumentSample: sampleFidelity === "exact_open_sample",
    sampleFidelity,
    playableStatus: sampleFidelity === "exact_open_sample" ? "ready_real_sample" : "ready_soundfont_proxy",
    audioLicense: "FluidR3 GM SoundFont sample",
    audioClassroomNote,
  };
}
