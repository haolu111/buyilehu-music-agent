import {
  buildGroupRelayRounds,
  hasMusicEvidence,
  judgeGroupRelay,
  markGroupPerformed,
  submitGroupAssessment,
  updateRelayEvidence
} from "../src/activity/groupRelayLogic";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
  }
}

const rounds = buildGroupRelayRounds(["A组拍第一小节", "B组接第二小节", "C组做休止动作"]);
assertEqual(rounds.length, 3, "one round is created for each group task");
assertEqual(rounds[0].status, "active", "first group starts active");
assertEqual(rounds[1].status, "waiting", "second group waits");
assertEqual(rounds[0].groupName, "A组", "group name is parsed from task");

const performed = markGroupPerformed(rounds, 0);
assertEqual(performed[0].status, "performed", "active group can mark performance complete");

const genericEvidence = updateRelayEvidence(performed, 0, "很好听，我喜欢");
const rejected = submitGroupAssessment(genericEvidence, 0);
assertEqual(rejected[0].status, "performed", "generic praise does not assess the group");
assertEqual(judgeGroupRelay(rejected).status, "needs_music_evidence", "generic praise asks for music evidence");

const musicEvidence = updateRelayEvidence(performed, 0, "节奏稳定，进入整齐");
const advanced = submitGroupAssessment(musicEvidence, 0);
assertEqual(advanced[0].status, "assessed", "music evidence assesses the current group");
assertEqual(advanced[1].status, "active", "next group becomes active after evidence");

let completed = submitGroupAssessment(
  updateRelayEvidence(markGroupPerformed(advanced, 1), 1, "能听同伴，节奏合拍"),
  1
);
completed = submitGroupAssessment(
  updateRelayEvidence(markGroupPerformed(completed, 2), 2, "休止能停住，速度稳定"),
  2
);
assertEqual(judgeGroupRelay(completed).status, "ready", "all assessed groups complete the relay");

assertEqual(hasMusicEvidence("我喜欢"), false, "generic preference is not music evidence");
assertEqual(hasMusicEvidence("节奏稳定"), true, "music term is accepted as evidence");
