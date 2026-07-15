import {
  buildEvidenceTerms,
  buildExitTicketExport,
  buildExitTicketSentence,
  summarizeExitTickets,
  judgeExitTicket
} from "../src/activity/exitTicketLogic";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
  }
}

const terms = buildEvidenceTerms(["能说出本课音乐要素", "能给出听到的依据"], "曲式中的重复、对比和再现");
assertEqual(terms.includes("重复/对比"), true, "曲式 focus creates repeat/contrast evidence");

assertEqual(
  judgeExitTicket({ focus: "", selectedEvidence: "重复/对比", reason: "A段回来了" }).status,
  "needs_focus",
  "exit ticket requires music focus"
);

assertEqual(
  judgeExitTicket({ focus: "曲式中的重复、对比和再现", selectedEvidence: "", reason: "A段回来了" }).status,
  "needs_evidence",
  "exit ticket requires evidence term"
);

assertEqual(
  judgeExitTicket({ focus: "曲式中的重复、对比和再现", selectedEvidence: "重复/对比", reason: "好听" }).status,
  "needs_reason",
  "generic reason is rejected"
);

assertEqual(
  judgeExitTicket({ focus: "曲式中的重复、对比和再现", selectedEvidence: "重复/对比", reason: "A段主题在最后又回来了" }).status,
  "ready",
  "specific music reason passes"
);

assertEqual(
  buildExitTicketSentence("稳定拍", "节奏稳定", "我能跟着拍点拍手"),
  "今天我理解了稳定拍，我的依据是节奏稳定：我能跟着拍点拍手。",
  "exit ticket sentence is classroom-readable"
);

const summary = summarizeExitTickets([
  {
    focus: "曲式中的重复、对比和再现",
    selectedEvidence: "重复/对比",
    reason: "A段主题在最后又回来了",
    submittedAt: "2026-06-07T04:00:00.000Z"
  },
  {
    focus: "曲式中的重复、对比和再现",
    selectedEvidence: "重复/对比",
    reason: "B段声音更轻，和A段不一样",
    submittedAt: "2026-06-07T04:01:00.000Z"
  },
  {
    focus: "曲式中的重复、对比和再现",
    selectedEvidence: "旋律走向",
    reason: "旋律后来往上走",
    submittedAt: "2026-06-07T04:02:00.000Z"
  }
]);

assertEqual(summary.total, 3, "summary counts submitted exit tickets");
assertEqual(summary.evidenceCounts["重复/对比"], 2, "summary counts evidence terms");
assertEqual(summary.topEvidence, "重复/对比", "summary finds top evidence");
assertEqual(summary.reviewSuggestion.includes("重复/对比"), true, "summary suggests next review focus");

const exported = JSON.parse(buildExitTicketExport(summary));
assertEqual(exported.version, "exit_ticket_class_summary_v1", "export has stable version");
assertEqual(exported.total, 3, "export keeps total");
