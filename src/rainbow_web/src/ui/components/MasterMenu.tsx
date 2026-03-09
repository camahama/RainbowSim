import type { SimulationId } from '../../app/registry';
import { SIMULATIONS } from '../../app/registry';

type MasterMenuProps = {
  activeId: SimulationId;
  onPick: (id: SimulationId) => void;
};

export function MasterMenu({ activeId, onPick }: MasterMenuProps) {
  return (
    <section className="menu-grid" aria-label="Simulation menu">
      {SIMULATIONS.map((sim) => {
        const active = sim.id === activeId;
        const disabled = sim.status !== 'ready';

        return (
          <button
            key={sim.id}
            type="button"
            className={`menu-card ${active ? 'active' : ''}`}
            onClick={() => !disabled && onPick(sim.id)}
            disabled={disabled}
            aria-current={active ? 'true' : undefined}
          >
            <span className="menu-title">{sim.title}</span>
            <span className="menu-subtitle">{sim.subtitle}</span>
            <span className={`badge ${sim.status}`}>{sim.status}</span>
          </button>
        );
      })}
    </section>
  );
}
