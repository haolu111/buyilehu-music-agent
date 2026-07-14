export type TouchShape =
  | { type: "rect"; x: number; y: number; width: number; height: number }
  | { type: "circle"; cx: number; cy: number; radius: number }
  | { type: "ellipse"; cx: number; cy: number; rx: number; ry: number }
  | { type: "ring"; cx: number; cy: number; innerRadius: number; outerRadius: number }
  | { type: "polygon"; points: Array<[number, number]> };

export type InstrumentTouchRegion = {
  id: string;
  instrumentId: string;
  zoneId: string;
  shape: TouchShape;
  gesture: "tap" | "hold_roll" | "choke";
  priority: number;
  accessibleLabel: string;
  hitSurface?: "skin_alpha" | "semantic_shape" | "visible_control";
};

export const INSTRUMENT_TOUCH_REGIONS: InstrumentTouchRegion[] = [
  { id: "frame-center", instrumentId: "virtual_frame_drum", zoneId: "center", shape: { type: "circle", cx: .502, cy: .511, radius: .28 }, gesture: "tap", priority: 20, accessibleLabel: "手鼓鼓心", hitSurface: "skin_alpha" },
  { id: "frame-edge", instrumentId: "virtual_frame_drum", zoneId: "edge", shape: { type: "ring", cx: .502, cy: .511, innerRadius: .28, outerRadius: .43 }, gesture: "tap", priority: 10, accessibleLabel: "手鼓鼓边", hitSurface: "skin_alpha" },
  { id: "snare-center", instrumentId: "virtual_snare_drum", zoneId: "center", shape: { type: "circle", cx: .506, cy: .543, radius: .25 }, gesture: "tap", priority: 20, accessibleLabel: "小鼓鼓心", hitSurface: "skin_alpha" },
  { id: "snare-rim", instrumentId: "virtual_snare_drum", zoneId: "rim", shape: { type: "ring", cx: .506, cy: .543, innerRadius: .25, outerRadius: .39 }, gesture: "tap", priority: 10, accessibleLabel: "小鼓边击", hitSurface: "skin_alpha" },
  { id: "woodblock-low", instrumentId: "virtual_woodblock", zoneId: "low", shape: { type: "rect", x: .04, y: .34, width: .61, height: .3 }, gesture: "tap", priority: 10, accessibleLabel: "左侧大型低音木鱼", hitSurface: "skin_alpha" },
  { id: "woodblock-high", instrumentId: "virtual_woodblock", zoneId: "high", shape: { type: "rect", x: .65, y: .37, width: .32, height: .25 }, gesture: "tap", priority: 10, accessibleLabel: "右侧小型高音木鱼", hitSurface: "skin_alpha" },
  { id: "shaker-tap", instrumentId: "virtual_shaker", zoneId: "short", shape: { type: "rect", x: .25, y: .12, width: .53, height: .78 }, gesture: "tap", priority: 20, accessibleLabel: "沙锤轻点", hitSurface: "skin_alpha" },
  { id: "shaker-roll", instrumentId: "virtual_shaker", zoneId: "sustain", shape: { type: "rect", x: .25, y: .12, width: .53, height: .78 }, gesture: "hold_roll", priority: 10, accessibleLabel: "沙锤长按滚奏", hitSurface: "skin_alpha" },
  { id: "triangle-choke", instrumentId: "virtual_triangle", zoneId: "dampen", shape: { type: "rect", x: .78, y: .04, width: .18, height: .14 }, gesture: "choke", priority: 30, accessibleLabel: "三角铁按住止音", hitSurface: "visible_control" },
  { id: "triangle-open", instrumentId: "virtual_triangle", zoneId: "open", shape: { type: "polygon", points: [[.52,.08],[.14,.84],[.9,.84]] }, gesture: "tap", priority: 10, accessibleLabel: "三角铁开放音", hitSurface: "semantic_shape" },
  { id: "tambourine-hit", instrumentId: "virtual_tambourine", zoneId: "hit", shape: { type: "circle", cx: .502, cy: .52, radius: .4 }, gesture: "tap", priority: 20, accessibleLabel: "铃鼓轻点", hitSurface: "skin_alpha" },
  { id: "tambourine-roll", instrumentId: "virtual_tambourine", zoneId: "roll", shape: { type: "circle", cx: .502, cy: .52, radius: .4 }, gesture: "hold_roll", priority: 10, accessibleLabel: "铃鼓长按滚奏", hitSurface: "skin_alpha" },
];

function inUnit(value: number): boolean { return Number.isFinite(value) && value >= 0 && value <= 1; }

export function validateTouchRegions(regions: InstrumentTouchRegion[]): true {
  const ids = new Set<string>();
  for (const region of regions) {
    if (!region.id || ids.has(region.id)) throw new Error(`Duplicate touch region: ${region.id}`);
    ids.add(region.id);
    const shape = region.shape;
    const values = shape.type === "rect" ? [shape.x, shape.y, shape.width, shape.height]
      : shape.type === "circle" ? [shape.cx, shape.cy, shape.radius]
      : shape.type === "ellipse" ? [shape.cx, shape.cy, shape.rx, shape.ry]
      : shape.type === "ring" ? [shape.cx, shape.cy, shape.innerRadius, shape.outerRadius]
      : shape.points.flat();
    if (!values.every(inUnit)) throw new Error(`Touch region outside normalized coordinates: ${region.id}`);
    if (shape.type === "ring" && shape.innerRadius >= shape.outerRadius) throw new Error(`Invalid ring: ${region.id}`);
  }
  return true;
}

export function pointInTouchShape(shape: TouchShape, x: number, y: number): boolean {
  if (!inUnit(x) || !inUnit(y)) return false;
  if (shape.type === "rect") return x >= shape.x && x <= shape.x + shape.width && y >= shape.y && y <= shape.y + shape.height;
  if (shape.type === "circle") return Math.hypot(x - shape.cx, y - shape.cy) <= shape.radius;
  if (shape.type === "ellipse") return ((x - shape.cx) / shape.rx) ** 2 + ((y - shape.cy) / shape.ry) ** 2 <= 1;
  if (shape.type === "ring") {
    const distance = Math.hypot(x - shape.cx, y - shape.cy);
    return distance >= shape.innerRadius && distance <= shape.outerRadius;
  }
  let inside = false;
  for (let index = 0, previous = shape.points.length - 1; index < shape.points.length; previous = index++) {
    const [xi, yi] = shape.points[index]; const [xj, yj] = shape.points[previous];
    if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
}

export function listInstrumentTouchRegions(instrumentId: string): InstrumentTouchRegion[] {
  return INSTRUMENT_TOUCH_REGIONS.filter((region) => region.instrumentId === instrumentId).sort((a, b) => b.priority - a.priority);
}

export function hitTestInstrumentTouchRegions(instrumentId: string, x: number, y: number, gesture: "tap" | "hold_roll" | "choke" = "tap"): InstrumentTouchRegion | null {
  const regions = listInstrumentTouchRegions(instrumentId);
  return regions.find((region) => pointInTouchShape(region.shape, x, y) && (gesture === "tap" ? region.gesture !== "hold_roll" : region.gesture === gesture)) ?? null;
}

validateTouchRegions(INSTRUMENT_TOUCH_REGIONS);
