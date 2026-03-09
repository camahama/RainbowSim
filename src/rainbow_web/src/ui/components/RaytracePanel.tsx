import { useMemo, useState } from 'react';
import { RaytraceSimulation } from '../../simulations/raytrace/raytraceSimulation';

const sim = new RaytraceSimulation();

function intensityToOpacity(intensity: number): number {
  return Math.min(1, Math.max(0.08, Math.sqrt(intensity)));
}

export function RaytracePanel() {
  const [sourceXOffset, setSourceXOffset] = useState(sim.getState().sourceXOffset);
  const [maxDepth, setMaxDepth] = useState(sim.getState().maxDepth);
  const [radius, setRadius] = useState(sim.getState().radius);

  const snapshot = useMemo(() => {
    sim.setSourceXOffset(sourceXOffset);
    sim.setMaxDepth(maxDepth);
    sim.setRadius(radius);
    return sim.compute();
  }, [sourceXOffset, maxDepth, radius]);

  return (
    <section className="panel">
      <h2>Raytrace Lab</h2>
      <p className="panel-lead">Recursive Fresnel split in a droplet-like sphere (reflection + transmission).</p>

      <div className="controls">
        <label>
          Source offset X: <strong>{sourceXOffset.toFixed(0)} px</strong>
          <input
            type="range"
            min={-420}
            max={420}
            step={1}
            value={sourceXOffset}
            onChange={(e) => setSourceXOffset(Number(e.target.value))}
          />
        </label>

        <label>
          Max recursion depth: <strong>{maxDepth}</strong>
          <input
            type="range"
            min={2}
            max={18}
            step={1}
            value={maxDepth}
            onChange={(e) => setMaxDepth(Number(e.target.value))}
          />
        </label>

        <label>
          Droplet radius: <strong>{radius.toFixed(0)} px</strong>
          <input
            type="range"
            min={80}
            max={230}
            step={1}
            value={radius}
            onChange={(e) => setRadius(Number(e.target.value))}
          />
        </label>
      </div>

      <div className="prism-canvas-wrap">
        <svg viewBox="0 0 1000 520" className="prism-canvas" role="img" aria-label="Recursive ray tracing in spherical drop">
          <rect x="0" y="0" width="1000" height="520" fill="#0a1017" />

          <circle
            cx={snapshot.center.x}
            cy={snapshot.center.y}
            r={snapshot.radius}
            fill="rgba(40, 60, 95, 0.35)"
            stroke="rgba(140, 190, 240, 0.78)"
            strokeWidth={2}
          />

          {snapshot.segments.map((seg, index) => (
            <line
              key={`${index}-${seg.start.x.toFixed(2)}`}
              className="additive-ray"
              x1={seg.start.x}
              y1={seg.start.y}
              x2={seg.end.x}
              y2={seg.end.y}
              stroke="rgb(255,245,210)"
              strokeWidth={2.8}
              strokeLinecap="round"
              opacity={intensityToOpacity(seg.intensity)}
            />
          ))}

          <circle cx={snapshot.source.x} cy={508} r={7} fill="#fff8cc" stroke="#ffffff" strokeWidth={1} />
        </svg>
      </div>
    </section>
  );
}
