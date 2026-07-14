type PointerStart = {
  pointerId: number;
  pressure: number;
  target: unknown;
};

type PointerEnd = {
  pointerId: number;
};

type ActivePointer = {
  zoneId: string;
  midi: number;
};

type PointerPerformanceOptions = {
  resolveZone: (target: unknown) => string | null;
  getMidiForZone: (zoneId: string) => number;
  noteOn: (midi: number, velocity: number, zoneId: string) => void;
  noteOff: (midi: number, zoneId: string) => void;
  defaultVelocity?: number;
  maxPointers?: number;
};

export class PointerPerformanceController {
  private readonly activePointers = new Map<number, ActivePointer>();
  private readonly defaultVelocity: number;
  private readonly maxPointers: number;

  constructor(private readonly options: PointerPerformanceOptions) {
    this.defaultVelocity = options.defaultVelocity ?? 96;
    this.maxPointers = options.maxPointers ?? 10;
  }

  pointerDown(event: PointerStart): boolean {
    if (this.activePointers.has(event.pointerId) || this.activePointers.size >= this.maxPointers) return false;
    const zoneId = this.options.resolveZone(event.target);
    if (!zoneId) return false;
    const midi = this.options.getMidiForZone(zoneId);
    const velocity = event.pressure > 0 ? Math.round(Math.max(0, Math.min(1, event.pressure)) * 127) : this.defaultVelocity;
    this.activePointers.set(event.pointerId, { zoneId, midi });
    this.options.noteOn(midi, velocity, zoneId);
    return true;
  }

  pointerMove(event: PointerStart): boolean {
    const active = this.activePointers.get(event.pointerId);
    if (!active) return false;
    const zoneId = this.options.resolveZone(event.target);
    if (!zoneId || zoneId === active.zoneId) return false;
    const midi = this.options.getMidiForZone(zoneId);
    this.options.noteOff(active.midi, active.zoneId);
    const velocity = event.pressure > 0 ? Math.round(Math.max(0, Math.min(1, event.pressure)) * 127) : this.defaultVelocity;
    this.activePointers.set(event.pointerId, { zoneId, midi });
    this.options.noteOn(midi, velocity, zoneId);
    return true;
  }

  pointerUp(event: PointerEnd): boolean {
    const active = this.activePointers.get(event.pointerId);
    if (!active) return false;
    this.activePointers.delete(event.pointerId);
    this.options.noteOff(active.midi, active.zoneId);
    return true;
  }

  pointerCancel(event: PointerEnd): boolean {
    return this.pointerUp(event);
  }

  cancelAll(): void {
    for (const active of this.activePointers.values()) this.options.noteOff(active.midi, active.zoneId);
    this.activePointers.clear();
  }

  get activePointerCount(): number {
    return this.activePointers.size;
  }
}
