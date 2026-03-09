import { useMemo, useState } from 'react';
import { RefractionSimulation } from '../../simulations/refraction/refractionSimulation';

const sim = new RefractionSimulation();

function fmt(value: number, digits = 2): string {
  return value.toFixed(digits);
}

export function RefractionPanel() {
  const [incidentDeg, setIncidentDeg] = useState(sim.getState().incidentDeg);
  const [n1, setN1] = useState(sim.getState().n1);
  const [n2, setN2] = useState(sim.getState().n2);

  const result = useMemo(() => {
    sim.setIncidentDeg(incidentDeg);
    sim.setMediumIndices(n1, n2);
    return sim.compute();
  }, [incidentDeg, n1, n2]);

  return (
    <section className="panel">
      <h2>Refraction Lab</h2>
      <p className="panel-lead">Phase 1 component. Physics is pure, simulation state is isolated.</p>

      <div className="controls">
        <label>
          Incident angle: <strong>{fmt(incidentDeg, 1)} deg</strong>
          <input
            type="range"
            min={0}
            max={89}
            step={0.1}
            value={incidentDeg}
            onChange={(e) => setIncidentDeg(Number(e.target.value))}
          />
        </label>

        <label>
          Medium 1 index (n1): <strong>{fmt(n1)}</strong>
          <input
            type="range"
            min={1}
            max={2}
            step={0.01}
            value={n1}
            onChange={(e) => setN1(Number(e.target.value))}
          />
        </label>

        <label>
          Medium 2 index (n2): <strong>{fmt(n2)}</strong>
          <input
            type="range"
            min={1}
            max={2}
            step={0.01}
            value={n2}
            onChange={(e) => setN2(Number(e.target.value))}
          />
        </label>
      </div>

      <div className="stats">
        <div>
          <span>Refracted angle</span>
          <strong>{result.tir ? 'Total internal reflection' : `${fmt(result.refractedDeg ?? 0, 2)} deg`}</strong>
        </div>
        <div>
          <span>Critical angle</span>
          <strong>{result.criticalAngleDeg === null ? 'Not applicable' : `${fmt(result.criticalAngleDeg, 2)} deg`}</strong>
        </div>
        <div>
          <span>Estimated reflectance</span>
          <strong>{fmt(result.reflectance * 100, 1)}%</strong>
        </div>
      </div>
    </section>
  );
}
