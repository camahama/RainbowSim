import { useMemo, useState } from 'react';
import { impactFromU, RAINBOW_BANDS } from '../../physics/droplet/engine';
import { DropletSimulation } from '../../simulations/droplet/dropletSimulation';

const sim = new DropletSimulation();

function toPolyline(points: { x: number; y: number }[]): string {
  return points.map((p) => `${p.x},${p.y}`).join(' ');
}

export function DropletPanel() {
  const initial = sim.getState();

  const [visible, setVisible] = useState<boolean[]>(initial.visible);
  const [focusedIndex, setFocusedIndex] = useState<number>(initial.focusedIndex);
  const [showPrimary, setShowPrimary] = useState<boolean>(initial.showPrimary);
  const [showSecondary, setShowSecondary] = useState<boolean>(initial.showSecondary);
  const [radius, setRadius] = useState<number>(initial.radius);
  const [primaryU, setPrimaryU] = useState<number[]>([...initial.primaryU]);
  const [secondaryU, setSecondaryU] = useState<number[]>([...initial.secondaryU]);

  const snapshot = useMemo(() => {
    for (let i = 0; i < visible.length; i += 1) {
      sim.setVisible(i, visible[i]);
    }
    sim.setFocusedIndex(focusedIndex);
    sim.setShowPrimary(showPrimary);
    sim.setShowSecondary(showSecondary);
    sim.setRadius(radius);
    for (let i = 0; i < primaryU.length; i += 1) {
      sim.setPrimaryU(i, primaryU[i]);
      sim.setSecondaryU(i, secondaryU[i]);
    }
    return sim.compute();
  }, [visible, focusedIndex, showPrimary, showSecondary, radius, primaryU, secondaryU]);

  const primaryImpactU = primaryU[focusedIndex];
  const secondaryImpactU = secondaryU[focusedIndex];
  const primaryImpactPx = impactFromU(primaryImpactU, snapshot.layout.radius);
  const secondaryImpactPx = impactFromU(secondaryImpactU, snapshot.layout.radius);

  return (
    <section className="panel">
      <h2>Droplet Lab</h2>
      <p className="panel-lead">Primary/secondary rainbow paths with wavelength-dependent refractive index.</p>

      <div className="controls droplet-controls">
        <div className="mode-row" role="group" aria-label="Ray families">
          <button
            type="button"
            className={showPrimary ? 'mode-btn active' : 'mode-btn'}
            onClick={() => setShowPrimary((v) => !v)}
          >
            Primary {showPrimary ? 'ON' : 'OFF'}
          </button>
          <button
            type="button"
            className={showSecondary ? 'mode-btn active' : 'mode-btn'}
            onClick={() => setShowSecondary((v) => !v)}
          >
            Secondary {showSecondary ? 'ON' : 'OFF'}
          </button>
          <button
            type="button"
            className="mode-btn"
            onClick={() => {
              sim.optimizeImpacts();
              const st = sim.getState();
              setPrimaryU([...st.primaryU]);
              setSecondaryU([...st.secondaryU]);
              setShowPrimary(st.showPrimary);
              setShowSecondary(st.showSecondary);
            }}
          >
            Optimize Angles
          </button>
        </div>

        <label>
          Focus color
          <select
            value={focusedIndex}
            onChange={(e) => {
              const idx = Number(e.target.value);
              setFocusedIndex(idx);
            }}
          >
            {RAINBOW_BANDS.map((band, idx) => (
              <option key={band.name} value={idx}>
                {band.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Droplet radius: <strong>{radius.toFixed(0)} px</strong>
          <input
            type="range"
            min={80}
            max={240}
            step={1}
            value={radius}
            onChange={(e) => setRadius(Number(e.target.value))}
          />
        </label>

        <label>
          Primary impact u: <strong>{primaryImpactU.toFixed(3)}</strong> ({primaryImpactPx.toFixed(1)} px)
          <input
            type="range"
            min={0}
            max={0.999}
            step={0.001}
            value={primaryImpactU}
            onChange={(e) => {
              const next = [...primaryU];
              next[focusedIndex] = Number(e.target.value);
              setPrimaryU(next);
            }}
          />
        </label>

        <label>
          Secondary impact u: <strong>{secondaryImpactU.toFixed(3)}</strong> ({secondaryImpactPx.toFixed(1)} px)
          <input
            type="range"
            min={0}
            max={0.999}
            step={0.001}
            value={secondaryImpactU}
            onChange={(e) => {
              const next = [...secondaryU];
              next[focusedIndex] = Number(e.target.value);
              setSecondaryU(next);
            }}
          />
        </label>
      </div>

      <div className="visibility-grid">
        {RAINBOW_BANDS.map((band, idx) => (
          <label key={band.name} className="vis-item">
            <input
              type="checkbox"
              checked={visible[idx]}
              onChange={(e) => {
                const next = [...visible];
                next[idx] = e.target.checked;
                setVisible(next);
              }}
            />
            <span className="swatch" style={{ backgroundColor: band.hex }} />
            {band.name}
          </label>
        ))}
      </div>

      <div className="prism-canvas-wrap">
        <svg viewBox="0 0 1000 560" className="prism-canvas" role="img" aria-label="Droplet primary and secondary ray paths">
          <rect x="0" y="0" width="1000" height="560" fill="#111720" />
          <circle
            cx={snapshot.layout.center.x}
            cy={snapshot.layout.center.y}
            r={snapshot.layout.radius}
            fill="rgba(35, 42, 90, 0.4)"
            stroke="rgba(210, 220, 245, 0.85)"
            strokeWidth={2}
          />

          {snapshot.rays.map((ray) => {
            const band = RAINBOW_BANDS[ray.bandIndex];
            const focused = ray.bandIndex === focusedIndex;
            const width = focused ? 3.8 : 2.2;
            const opacity = focused ? 1 : 0.7;

            return (
              <g key={band.name}>
                {ray.primary?.points.length ? (
                  <polyline
                    className="additive-ray"
                    points={toPolyline(ray.primary.points)}
                    fill="none"
                    stroke={band.hex}
                    strokeWidth={width}
                    opacity={opacity}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                ) : null}
                {ray.secondary?.points.length ? (
                  <polyline
                    className="additive-ray"
                    points={toPolyline(ray.secondary.points)}
                    fill="none"
                    stroke={band.hex}
                    strokeWidth={width}
                    opacity={opacity}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeDasharray="7 5"
                  />
                ) : null}
              </g>
            );
          })}
        </svg>
      </div>

      <div className="stats">
        <div>
          <span>Focused color</span>
          <strong>{RAINBOW_BANDS[focusedIndex].name}</strong>
        </div>
        <div>
          <span>Primary deflection</span>
          <strong>
            {snapshot.focusedPrimaryDeviation === null ? 'N/A' : `${snapshot.focusedPrimaryDeviation.toFixed(1)}°`}
          </strong>
        </div>
        <div>
          <span>Secondary deflection</span>
          <strong>
            {snapshot.focusedSecondaryDeviation === null ? 'N/A' : `${snapshot.focusedSecondaryDeviation.toFixed(1)}°`}
          </strong>
        </div>
      </div>
    </section>
  );
}
