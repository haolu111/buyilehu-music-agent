import {
  buildDefaultInstrumentCards,
  judgeInstrumentFamilySort
} from "../src/activity/instrumentFamilyLogic";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
  }
}

const cards = buildDefaultInstrumentCards(["笛子", "二胡", "琵琶", "小鼓"], ["吹奏", "拉弦", "弹拨", "打击"]);
assertEqual(cards[0].family, "吹奏", "笛子 maps to blowing family");
assertEqual(cards[1].family, "拉弦", "二胡 maps to bowed-string family");
assertEqual(cards[2].family, "弹拨", "琵琶 maps to plucked-string family");
assertEqual(cards[3].family, "打击", "小鼓 maps to percussion family");
assertEqual(cards[0].visualSourceStatus, "generated_illustration", "笛子 uses generated playable skin instead of web photos");
assertEqual(cards[0].imageUrl?.endsWith("/generated_playable_instrument_pack/images/dizi_playable_board.png"), true, "笛子 points to generated playable skin PNG");
assertEqual(cards[1].visualSourceStatus, "pending_generated_skin", "二胡 waits for generated playable skin instead of web photos");
assertEqual(cards[2].visualSourceStatus, "pending_generated_skin", "琵琶 waits for generated playable skin instead of web photos");
assertEqual(cards[3].visualSourceStatus, "generated_illustration", "小鼓 uses generated playable skin");
assertEqual(cards[3].imageUrl?.endsWith("/generated_playable_instrument_pack/images/virtual_hand_drum.png"), true, "小鼓 points to generated playable skin PNG");
assertEqual(cards[0].audioSourceKind, "open_sample", "笛子 uses sample-backed playback");
assertEqual(cards[0].playbackInstrument, "flute", "笛子 maps to flute playback");
assertEqual(cards[3].audioSourceKind, "open_sample", "小鼓 uses sampled drum playback");
assertEqual(cards[3].playbackInstrument, "taiko_drum", "小鼓 maps to local sampled drum playback");
assertEqual(cards[0].isRealSample, true, "sample-backed playback is marked as real sample");
assertEqual(cards[0].exactRealInstrumentSample, false, "笛子 does not claim exact real dizi sampling yet");
assertEqual(cards[0].sampleFidelity, "approximate_soundfont_sample", "笛子 is marked as approximate sampled proxy");
assertEqual(cards[0].playableStatus, "ready_soundfont_proxy", "笛子 is playable but still needs exact sample");
assertEqual(cards[0].audioClassroomNote.includes("采样"), true, "audio source note is explicit");

const fluteCards = buildDefaultInstrumentCards(["长笛"], ["吹奏", "拉弦", "弹拨", "打击"]);
assertEqual(fluteCards[0].visualSourceStatus, "generated_illustration", "长笛 uses generated playable skin");
assertEqual(fluteCards[0].exactRealInstrumentSample, true, "长笛 can claim exact flute SoundFont sample");
assertEqual(fluteCards[0].sampleFidelity, "exact_open_sample", "长笛 is marked exact sample");

const firstPackCards = buildDefaultInstrumentCards(
  ["小鼓", "木鱼", "沙锤", "三角铁", "铃鼓", "音条琴", "竖笛", "口风琴", "笛子", "二胡", "琵琶"],
  ["吹奏", "拉弦", "弹拨", "打击"]
);
for (const card of firstPackCards) {
  assertEqual(Boolean(card.imageUrl?.includes("primary_instrument_card_pack")), false, `${card.label} does not use the old web-photo pack`);
  assertEqual(Boolean(card.imageUrl?.endsWith(".jpg")), false, `${card.label} does not use web-photo jpg assets`);
  assertEqual(card.audioSourceKind, "open_sample", `${card.label} uses the playable sample pack`);
  assertEqual(card.isRealSample, true, `${card.label} is sample-backed`);
  assertEqual(["ready_real_sample", "ready_soundfont_proxy"].includes(card.playableStatus), true, `${card.label} exposes playable sample status`);
}

assertEqual(
  judgeInstrumentFamilySort({
    card: cards[0],
    selectedFamily: "吹奏",
    selectedEvidence: ["气息感"],
    hasListened: false,
  }).status,
  "blocked_listen_first",
  "instrument family sorting requires listening before classifying"
);

assertEqual(
  judgeInstrumentFamilySort({
    card: cards[1],
    selectedFamily: "弹拨",
    selectedEvidence: ["拨弦"],
    hasListened: true,
  }).status,
  "wrong_family",
  "wrong family is rejected even with evidence"
);

assertEqual(
  judgeInstrumentFamilySort({
    card: cards[2],
    selectedFamily: "弹拨",
    selectedEvidence: [],
    hasListened: true,
  }).status,
  "needs_evidence",
  "correct family still needs musical evidence"
);

assertEqual(
  judgeInstrumentFamilySort({
    card: cards[3],
    selectedFamily: "打击",
    selectedEvidence: ["敲击感"],
    hasListened: true,
  }).status,
  "correct",
  "correct family and evidence passes"
);
