import {
  computePrismSnapshot,
  prismModeDescription,
  type PrismMode,
  type PrismSnapshot,
} from '../../physics/prism/engine';

export type PrismState = {
  mode: PrismMode;
  incidentDeg: number;
};

export class PrismSimulation {
  private state: PrismState;

  constructor(initial?: Partial<PrismState>) {
    this.state = {
      mode: initial?.mode ?? 'triangle',
      incidentDeg: initial?.incidentDeg ?? 0,
    };
  }

  setMode(mode: PrismMode): void {
    this.state.mode = mode;
  }

  setIncidentDeg(incidentDeg: number): void {
    this.state.incidentDeg = Math.max(-35, Math.min(35, incidentDeg));
  }

  getState(): PrismState {
    return { ...this.state };
  }

  description(): string {
    return prismModeDescription(this.state.mode);
  }

  compute(): PrismSnapshot {
    return computePrismSnapshot(this.state.mode, this.state.incidentDeg);
  }
}
