import { useState } from 'react';
import { MasterMenu } from './ui/components/MasterMenu';
import { RefractionPanel } from './ui/components/RefractionPanel';
import { PrismPanel } from './ui/components/PrismPanel';
import { RaytracePanel } from './ui/components/RaytracePanel';
import { DropletPanel } from './ui/components/DropletPanel';
import { Droplet2Panel } from './ui/components/Droplet2Panel';
import { RainbowPanel } from './ui/components/RainbowPanel';
import type { SimulationId } from './app/registry';
import { UI_TEXT } from './app/uiText';

function App() {
  const [activeId, setActiveId] = useState<SimulationId | null>(null);

  const isMenu = activeId === null;

  return (
    <div className="presentation-root">
      <div className="stage">
        <div className="stage-scroll">
          {isMenu ? (
            <header className="hero">
              <h1>{UI_TEXT.appTitle}</h1>
              <p className="hero-copy">{UI_TEXT.appSubtitle}</p>
              <MasterMenu activeId={activeId} onPick={setActiveId} />
            </header>
          ) : (
            <main className="workspace">
              <button type="button" className="menu-return-btn" onClick={() => setActiveId(null)}>
                {UI_TEXT.menuButton}
              </button>

              {activeId === 'refraction' ? <RefractionPanel /> : null}
              {activeId === 'prism' ? <PrismPanel /> : null}
              {activeId === 'raytrace' ? <RaytracePanel /> : null}
              {activeId === 'droplet' ? <DropletPanel /> : null}
              {activeId === 'droplet2' ? <Droplet2Panel /> : null}
              {activeId === 'rainbow' ? <RainbowPanel /> : null}

              {activeId !== 'refraction' &&
              activeId !== 'prism' &&
              activeId !== 'raytrace' &&
              activeId !== 'droplet' &&
              activeId !== 'droplet2' &&
              activeId !== 'rainbow' ? (
                <section className="panel">
                  <h2>{UI_TEXT.fallbackTitle}</h2>
                  <p className="panel-lead">{UI_TEXT.fallbackBody}</p>
                </section>
              ) : null}
            </main>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
