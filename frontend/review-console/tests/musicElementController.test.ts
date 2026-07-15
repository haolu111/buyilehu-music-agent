import assert from "node:assert/strict";
import {
  DEFAULT_MUSIC_ELEMENT_CONFIG,
  fileFromBoundSource,
  listeningFileKey,
  needsListeningUpload,
  transformListeningSession,
  uploadListeningSource
} from "../src/music-components/musicElementController";

const lessonFile = new File(["classroom-audio"], "lesson.wav", {
  type: "audio/wav",
  lastModified: 1234
});

assert.equal(listeningFileKey(lessonFile), `lesson.wav:${lessonFile.size}:1234`);
assert.equal(needsListeningUpload(listeningFileKey(lessonFile), "", ""), true);
assert.equal(needsListeningUpload(listeningFileKey(lessonFile), "session-1", listeningFileKey(lessonFile)), false);
assert.equal(needsListeningUpload(listeningFileKey(lessonFile), "session-1", "other.wav:1:2"), true);
assert.deepEqual(DEFAULT_MUSIC_ELEMENT_CONFIG, {
  tonic: "C",
  mode: "preserve",
  tempoMultiplier: 1,
  rhythmDensity: "preserve",
  instrument: "preserve"
});

const requests: Array<{ url: string; form: FormData }> = [];
const successfulFetch = async (input: RequestInfo | URL, init?: RequestInit) => {
  requests.push({ url: String(input), form: init?.body as FormData });
  const payload = String(input).endsWith("/upload")
    ? { session_id: "session-1", source_audio_url: "/output/source.wav" }
    : { session_id: "session-1", transformed_audio_url: "/output/transformed.mp3", cache_hit: false };
  return new Response(JSON.stringify(payload), {
    status: 200,
    headers: { "Content-Type": "application/json" }
  });
};

const uploaded = await uploadListeningSource(lessonFile, successfulFetch);
assert.equal(uploaded.session_id, "session-1");
assert.equal(requests[0]?.url, "/api/listening/upload");
assert.equal(requests[0]?.form.get("audio"), lessonFile);

const transformed = await transformListeningSession(
  "session-1",
  {
    tonic: "G",
    mode: "western_major",
    tempoMultiplier: 0.8,
    rhythmDensity: "relaxed",
    instrument: "piano"
  },
  successfulFetch
);
assert.equal(transformed.transformed_audio_url, "/output/transformed.mp3");
assert.equal(requests[1]?.url, "/api/listening/transform");
assert.deepEqual(Object.fromEntries(requests[1]!.form.entries()), {
  session_id: "session-1",
  tonic: "G",
  mode: "western_major",
  tempo_multiplier: "0.8",
  rhythm_density: "relaxed",
  instrument: "piano"
});

await assert.rejects(
  () => uploadListeningSource(lessonFile, async () => new Response(JSON.stringify({ error: "无法解析歌曲" }), {
    status: 422,
    headers: { "Content-Type": "application/json" }
  })),
  /无法解析歌曲/
);

const boundFile = await fileFromBoundSource(
  { url: "/uploads/bound-song.mp3", label: "教师已绑定歌曲.mp3" },
  async (input) => {
    assert.equal(String(input), "/uploads/bound-song.mp3");
    return new Response(new Blob(["bound-audio"], { type: "audio/mpeg" }), { status: 200 });
  }
);
assert.equal(boundFile.name, "教师已绑定歌曲.mp3");
assert.equal(boundFile.type, "audio/mpeg");

await assert.rejects(
  () => fileFromBoundSource(
    { url: "https://example.com/cross-origin.mp3", label: "跨域歌曲.mp3" },
    async () => new Response("blocked", { status: 403 })
  ),
  /请重新上传/
);
