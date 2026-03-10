import {
  computePrismSnapshot,
  prismModeDescription,
  type PrismMode,
  type PrismSnapshot,
} from '../../physics/prism/engine';

export type PrismState = {
  mode: PrismMode;
  incidentDeg: number;
  colorSeparation: number;
};

export class PrismSimulation {
  private state: PrismState;

  constructor(initial?: Partial<PrismState>) {
    this.state = {
      mode: initial?.mode ?? 'triangle',
      incidentDeg: initial?.incidentDeg ?? 0,
      colorSeparation: initial?.colorSeparation ?? 0,
    };
  }

  setMode(mode: PrismMode): void {
    this.state.mode = mode;
  }

  setIncidentDeg(incidentDeg: number): void {
    this.state.incidentDeg = Math.max(-15, Math.min(15, incidentDeg));
  }

  setColorSeparation(value: number): void {
    this.state.colorSeparation = Math.max(0, Math.min(14, value));
  }

  getState(): PrismState {
    return { ...this.state };
  }

  description(): string {
    return prismModeDescription(this.state.mode);
  }

  compute(): PrismSnapshot {
    return computePrismSnapshot(this.state.mode, this.state.incidentDeg, this.state.colorSeparation);
  }
}
