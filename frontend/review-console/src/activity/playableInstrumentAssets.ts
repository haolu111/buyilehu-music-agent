export const GENERATED_PLAYABLE_INSTRUMENT_PACK_ID = "generated_playable_instrument_pack";
export const GENERATED_PLAYABLE_INSTRUMENT_BASE =
  `/static/assets/primary-asset-packs/${GENERATED_PLAYABLE_INSTRUMENT_PACK_ID}/images`;

export type PlayableInstrumentSkinStatus = "generated_illustration" | "pending_generated_skin";

export type PlayableInstrumentAsset = {
  assetId: string;
  label: string;
  packId: typeof GENERATED_PLAYABLE_INSTRUMENT_PACK_ID;
  status: PlayableInstrumentSkinStatus;
  url?: string;
};

const READY_GENERATED_SKINS = new Set([
  "rhythm_pad",
  "virtual_hand_drum",
  "woodblock_claves",
  "shaker",
  "triangle_bell",
  "tambourine",
  "virtual_xylophone",
  "simple_keyboard",
  "pentatonic_grid",
  "recorder_fingering_board",
  "melodica_keyboard_board",
  "dizi_playable_board",
  "flute_playable_board"
]);

const PLAYABLE_SKIN_ALIASES: Array<[string[], { assetId: string; label: string }]> = [
  [["rhythm_pad", "节奏垫", "节奏pad", "pad"], { assetId: "rhythm_pad", label: "节奏垫" }],
  [["virtual_hand_drum", "hand_drum", "小鼓", "手鼓", "鼓", "drum"], { assetId: "virtual_hand_drum", label: "虚拟小鼓" }],
  [["woodblock_claves", "woodblock", "claves", "木鱼", "响板"], { assetId: "woodblock_claves", label: "木鱼响板" }],
  [["shaker", "沙锤", "沙槌", "maraca"], { assetId: "shaker", label: "虚拟沙锤" }],
  [["triangle_bell", "triangle", "bell", "三角铁", "碰铃"], { assetId: "triangle_bell", label: "三角铁碰铃" }],
  [["tambourine", "铃鼓"], { assetId: "tambourine", label: "虚拟铃鼓" }],
  [["virtual_xylophone", "xylophone", "音条琴", "木琴"], { assetId: "virtual_xylophone", label: "虚拟音条琴" }],
  [["simple_keyboard", "keyboard", "piano", "钢琴", "键盘"], { assetId: "simple_keyboard", label: "简版键盘" }],
  [["pentatonic_grid", "五声", "五声宫格", "do re mi sol la"], { assetId: "pentatonic_grid", label: "五声宫格乐器" }],
  [["recorder_fingering_board", "recorder", "竖笛"], { assetId: "recorder_fingering_board", label: "竖笛指法板" }],
  [["melodica_keyboard_board", "melodica", "口风琴"], { assetId: "melodica_keyboard_board", label: "口风琴键盘板" }],
  [["dizi_playable_board", "dizi", "竹笛", "笛子"], { assetId: "dizi_playable_board", label: "笛子演奏板" }],
  [["flute_playable_board", "flute", "长笛"], { assetId: "flute_playable_board", label: "长笛演奏板" }]
];

export function playableInstrumentAssetFor(label = ""): PlayableInstrumentAsset {
  const normalized = normalizeInstrumentKey(label);
  if (isCompositePlayableInstrumentLabel(normalized)) {
    return {
      assetId: normalized || "unknown_playable_instrument",
      label: label || "待接入乐器",
      packId: GENERATED_PLAYABLE_INSTRUMENT_PACK_ID,
      status: "pending_generated_skin",
    };
  }
  const match = PLAYABLE_SKIN_ALIASES.find(([aliases]) =>
    aliases.some((alias) => normalized.includes(normalizeInstrumentKey(alias)))
  );
  const resolved = match?.[1] ?? { assetId: normalized || "unknown_playable_instrument", label: label || "待生成乐器" };
  const url = playableInstrumentAssetUrl(resolved.assetId);
  return {
    ...resolved,
    packId: GENERATED_PLAYABLE_INSTRUMENT_PACK_ID,
    status: url ? "generated_illustration" : "pending_generated_skin",
    url
  };
}

export function playableInstrumentAssetUrl(assetIdOrPath = ""): string | undefined {
  const value = String(assetIdOrPath || "").trim();
  if (!value || value.includes("primary_instrument_card_pack") || value.endsWith(".jpg")) return undefined;
  const assetId = value
    .replace(/^.*\/generated_playable_instrument_pack\/images\//, "")
    .replace(/\.png$/, "");
  if (!READY_GENERATED_SKINS.has(assetId)) return undefined;
  return `${GENERATED_PLAYABLE_INSTRUMENT_BASE}/${assetId}.png`;
}

function normalizeInstrumentKey(value: string) {
  return String(value || "").trim().toLowerCase().replace(/\s+/g, "_");
}

function isCompositePlayableInstrumentLabel(normalized: string) {
  return /(^|_)(kit|ensemble|controller|collection)(_|$)/.test(normalized);
}
