import { createRainbowView, rainbowPixelContribution, type RainbowView } from '../../physics/rainbow/engine';
import { UI_PARAMS } from '../../app/uiParams';

export type RainbowDrop = { x: number; y: number; color: string; intensity: number; radius: number };
export type RainbowDropSample = RainbowDrop & { r: number; g: number; b: number };

export type RainbowUiState = {
  simulating: boolean;
  pointsPerFrame: number;
  totalPoints: number;
};

export class RainbowSimulation {
  private view: RainbowView;
  private simulating = false;
  private pointsPerFrame: number = UI_PARAMS.rainbow.defaults.pointsPerFrame;
  private readonly acceleration: number = UI_PARAMS.rainbow.defaults.acceleration;
  private readonly maxPoints: number = UI_PARAMS.rainbow.defaults.maxPoints;
  private totalPoints = 0;

  constructor() {
    this.view = createRainbowView();
  }

  uiState(): RainbowUiState {
    return {
      simulating: this.simulating,
      pointsPerFrame: this.pointsPerFrame,
      totalPoints: this.totalPoints,
    };
  }

  viewState(): RainbowView {
    return this.view;
  }

  setSimulating(value: boolean): void {
    this.simulating = value;
  }

  toggleSimulating(): void {
    this.simulating = !this.simulating;
  }

  clear(): void {
    this.totalPoints = 0;
    this.pointsPerFrame = UI_PARAMS.rainbow.defaults.pointsPerFrame;
  }

  manualDrop(x: number, y: number, boost = false): RainbowDropSample | null {
    const c = rainbowPixelContribution(x, y, this.view, boost, { allowWeak: true });
    this.totalPoints += 1;

    if (!c || c.intensity <= UI_PARAMS.rainbow.intensityThreshold) {
      return null;
    }

    return {
      x,
      y,
      r: c.r,
      g: c.g,
      b: c.b,
      color: c.color,
      intensity: c.intensity,
      radius: boost ? UI_PARAMS.rainbow.manualDropRadius.boosted : UI_PARAMS.rainbow.manualDropRadius.normal,
    };
  }

  previewDrop(x: number, y: number): RainbowDropSample {
    const c = rainbowPixelContribution(x, y, this.view, false, { allowWeak: true });
    if (!c || c.intensity <= UI_PARAMS.rainbow.intensityThreshold) {
      return {
        x,
        y,
        r: 0,
        g: 0,
        b: 0,
        color: 'rgb(0, 0, 0)',
        intensity: 0,
        radius: UI_PARAMS.rainbow.previewRadius,
      };
    }

    return {
      x,
      y,
      r: c.r,
      g: c.g,
      b: c.b,
      color: c.color,
      intensity: c.intensity,
      radius: UI_PARAMS.rainbow.previewRadius,
    };
  }

  rainTick(): RainbowDropSample[] {
    if (!this.simulating) {
      return [];
    }

    const out: RainbowDropSample[] = [];
    const count = Math.max(0, Math.floor(this.pointsPerFrame));

    for (let i = 0; i < count; i += 1) {
      const x = Math.random() * this.view.config.width;
      const y = Math.random() * this.view.config.height;
      const c = rainbowPixelContribution(x, y, this.view, false);
      if (c) {
        out.push({
          x,
          y,
          r: c.r,
          g: c.g,
          b: c.b,
          color: c.color,
          intensity: c.intensity,
          radius: UI_PARAMS.rainbow.rainDropRadius,
        });
      }
    }

    this.pointsPerFrame = Math.min(this.maxPoints, this.pointsPerFrame * this.acceleration);
    this.totalPoints += count;

    return out;
  }
}
