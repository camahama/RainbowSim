import { useMemo, useState } from 'react';
import { PrismSimulation } from '../../simulations/prism/prismSimulation';
import type { PrismMode, Vec2 } from '../../physics/prism/engine';

const sim = new PrismSimulation();

function pointsToSvg(points: Vec2[]): string {
  return points.map((p) => `${p.x},${p.y}`).join(' ');
}

export function PrismPanel() {
  const [mode, setMode] = useState<PrismMode>(sim.getState().mode);
  const [incidentDeg, setIncidentDeg] = useState<number>(sim.getState().incidentDeg);

  const snapshot = useMemo(() => {
    sim.setMode(mode);
    sim.setIncidentDeg(incidentDeg);
    return sim.compute();
  }, [mode, incidentDeg]);

  const description = sim.description();

  return (
    <section className="panel prism-panel">
      <h2>Prism Lab</h2>
      <p className="panel-lead">Phase 2 component. Polygon ray tracing with wavelength-dependent indices.</p>

      <div className="controls prism-controls">
        <div className="mode-row" role="group" aria-label="Prism mode">
          <button type="button" className={mode === 'air' ? 'mode-btn active' : 'mode-btn'} onClick={() => setMode('air')}>
            Air
          </button>
          <button
            type="button"
            className={mode === 'block_straight' ? 'mode-btn active' : 'mode-btn'}
            onClick={() => setMode('block_straight')}
          >
            Straight
          </button>
          <button
            type="button"
            className={mode === 'block_rotated' ? 'mode-btn active' : 'mode-btn'}
            onClick={() => setMode('block_rotated')}
          >
            Rotated
          </button>
          <button
            type="button"
            className={mode === 'triangle' ? 'mode-btn active' : 'mode-btn'}
            onClick={() => setMode('triangle')}
          >
            Prism
          </button>
        </div>

        <label>
          Incoming angle: <strong>{incidentDeg.toFixed(1)} deg</strong>
          <input
            type="range"
            min={-35}
            max={35}
            step={0.5}
            value={incidentDeg}
            onChange={(e) => setIncidentDeg(Number(e.target.value))}
          />
        </label>
      </div>

      <p className="mode-description">{description}</p>

      <div className="prism-canvas-wrap">
        <svg viewBox="0 0 1000 460" className="prism-canvas" role="img" aria-label="Prism ray tracing visualization">
          <rect x="0" y="0" width="1000" height="460" fill="#0a0f14" />

          {snapshot.polygon.length > 0 ? (
            <polygon
              points={pointsToSvg(snapshot.polygon)}
              fill="rgba(110, 150, 190, 0.24)"
              stroke="rgba(180, 210, 240, 0.7)"
              strokeWidth={2}
            />
          ) : null}

          {snapshot.rays.map((ray) => (
            <polyline
              key={ray.band.name}
              points={pointsToSvg(ray.points)}
              fill="none"
              stroke={ray.band.color}
              strokeWidth={3.8}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          ))}
        </svg>
      </div>

      <div className="legend">
        {snapshot.rays.map((ray) => (
          <div key={ray.band.name} className="legend-item">
            <span className="swatch" style={{ backgroundColor: ray.band.color }} />
            <span>
              {ray.band.name} n={ray.band.n.toFixed(2)}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
