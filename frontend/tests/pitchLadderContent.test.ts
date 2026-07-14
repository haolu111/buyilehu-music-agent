import {
  buildPitchLadderNativeRoutePoints,
  usesNativePitchLadderMapRoute
} from "../src/student-game/pitchLadderContent";

function assertEqual(actual: unknown, expected: unknown, label: string) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
  }
}

function assert(condition: boolean, label: string) {
  if (!condition) throw new Error(label);
}

assertEqual(usesNativePitchLadderMapRoute("mountain", "map_native"), true, "mountain uses native route");
assertEqual(usesNativePitchLadderMapRoute("cloud", undefined), true, "missing route style keeps native route fallback");
assertEqual(usesNativePitchLadderMapRoute("bamboo", "floating_platforms"), false, "explicit floating platforms can opt out");
assertEqual(usesNativePitchLadderMapRoute("lantern", "map_native"), false, "lantern has no native asset route");

const melodyRoute = buildPitchLadderNativeRoutePoints(5, "mountain", 960, 540);
assertEqual(melodyRoute.length, 5, "native melody route has one point per pitch node");
assert(melodyRoute[0].x > 430 && melodyRoute[0].y > 420, "native route starts on the map entry");
assert(melodyRoute[4].x > 700 && melodyRoute[4].y < 90, "native route ends near the summit");
assert(melodyRoute[2].y < melodyRoute[0].y, "native route climbs upward across pitch nodes");
