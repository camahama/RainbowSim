import type { SimulationId } from '../../app/registry';
import { SIMULATION_IDS } from '../../app/registry';
import { UI_TEXT } from '../../app/uiText';

type MasterMenuProps = {
  activeId: SimulationId | null;
  onPick: (id: SimulationId) => void;
};

export function MasterMenu({ activeId, onPick }: MasterMenuProps) {
  return (
    <section className="menu-grid" aria-label={UI_TEXT.appSubtitle}>
      {SIMULATION_IDS.map((id) => {
        const active = id === activeId;
        return (
          <button
            key={id}
            type="button"
            className={`menu-card ${active ? 'active' : ''}`}
            onClick={() => onPick(id)}
            aria-current={active ? 'true' : undefined}
          >
            {UI_TEXT.moduleButtons[id]}
          </button>
        );
      })}
    </section>
  );
}
