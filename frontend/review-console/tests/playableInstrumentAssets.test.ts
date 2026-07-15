import {
  GENERATED_PLAYABLE_INSTRUMENT_PACK_ID,
  playableInstrumentAssetFor,
  playableInstrumentAssetUrl
} from "../src/activity/playableInstrumentAssets";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
  }
}

assertEqual(GENERATED_PLAYABLE_INSTRUMENT_PACK_ID, "generated_playable_instrument_pack", "generated pack id is stable");

const handDrum = playableInstrumentAssetFor("小鼓");
assertEqual(handDrum.assetId, "virtual_hand_drum", "小鼓 resolves to generated hand drum skin");
assertEqual(handDrum.status, "generated_illustration", "小鼓 generated skin is ready");
assertEqual(handDrum.url, "/static/assets/primary-asset-packs/generated_playable_instrument_pack/images/virtual_hand_drum.png", "小鼓 uses generated PNG path");

const xylophone = playableInstrumentAssetFor("音条琴");
assertEqual(xylophone.assetId, "virtual_xylophone", "音条琴 resolves to generated xylophone skin id");
assertEqual(xylophone.status, "generated_illustration", "音条琴 generated skin is ready");
assertEqual(xylophone.url, "/static/assets/primary-asset-packs/generated_playable_instrument_pack/images/virtual_xylophone.png", "音条琴 uses its own single-instrument skin");

const recorder = playableInstrumentAssetFor("竖笛");
assertEqual(recorder.assetId, "recorder_fingering_board", "竖笛 resolves to generated recorder skin id");
assertEqual(recorder.status, "generated_illustration", "竖笛 generated skin is ready");
assertEqual(recorder.url, "/static/assets/primary-asset-packs/generated_playable_instrument_pack/images/recorder_fingering_board.png", "竖笛 uses its own single-instrument skin");

const melodica = playableInstrumentAssetFor("口风琴");
assertEqual(melodica.assetId, "melodica_keyboard_board", "口风琴 resolves to generated melodica skin id");
assertEqual(melodica.status, "generated_illustration", "口风琴 generated skin is ready");
assertEqual(melodica.url, "/static/assets/primary-asset-packs/generated_playable_instrument_pack/images/melodica_keyboard_board.png", "口风琴 uses its own single-instrument skin");

const flute = playableInstrumentAssetFor("长笛");
assertEqual(flute.assetId, "flute_playable_board", "长笛 resolves to generated flute board skin id");
assertEqual(flute.status, "generated_illustration", "长笛 generated skin is ready");
assertEqual(flute.url, "/static/assets/primary-asset-packs/generated_playable_instrument_pack/images/flute_playable_board.png", "长笛 uses its own single-instrument skin");

const dizi = playableInstrumentAssetFor("笛子");
assertEqual(dizi.assetId, "dizi_playable_board", "笛子 resolves to generated dizi board skin id");
assertEqual(dizi.status, "generated_illustration", "笛子 generated skin is ready");
assertEqual(dizi.url, "/static/assets/primary-asset-packs/generated_playable_instrument_pack/images/dizi_playable_board.png", "笛子 uses its own single-instrument skin");

const percussionKit = playableInstrumentAssetFor("classroom_percussion_kit");
assertEqual(percussionKit.status, "pending_generated_skin", "percussion kit is not a single playable skin");
assertEqual(percussionKit.assetId, "classroom_percussion_kit", "percussion kit keeps its collection id");
assertEqual(percussionKit.url, undefined, "percussion kit does not use one combined image as a playable instrument");

const ensembleController = playableInstrumentAssetFor("ensemble_controller");
assertEqual(ensembleController.status, "pending_generated_skin", "ensemble controller is not a single playable skin");
assertEqual(ensembleController.url, undefined, "ensemble controller stays pending until a dedicated skin exists");

assertEqual(playableInstrumentAssetUrl("primary_instrument_card_pack/images/hand_drum.jpg"), undefined, "old web-photo paths are rejected");
