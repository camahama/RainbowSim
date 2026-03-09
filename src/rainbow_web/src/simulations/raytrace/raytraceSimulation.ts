import { computeRaytraceSnapshot, type RaytraceInput, type RaytraceSnapshot } from '../../physics/raytrace/engine';

export class RaytraceSimulation {
  private state: RaytraceInput;

  constructor(initial?: Partial<RaytraceInput>) {
    this.state = {
      sourceXOffset: initial?.sourceXOffset ?? -180,
      maxDepth: initial?.maxDepth ?? 12,
      minIntensity: initial?.minIntensity ?? 0.001,
      radius: initial?.radius ?? 180,
      nAir: initial?.nAir ?? 1,
      nWater: initial?.nWater ?? 1.333,
    };
  }

  setSourceXOffset(value: number): void {
    this.state.sourceXOffset = Math.max(-420, Math.min(420, value));
  }

  setMaxDepth(value: number): void {
    this.state.maxDepth = Math.max(2, Math.min(18, Math.round(value)));
  }

  setRadius(value: number): void {
    this.state.radius = Math.max(80, Math.min(230, value));
  }

  getState(): RaytraceInput {
    return { ...this.state };
  }

  compute(): RaytraceSnapshot {
    return computeRaytraceSnapshot(this.state);
  }
}
