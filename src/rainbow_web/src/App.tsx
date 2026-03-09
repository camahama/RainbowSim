import { useState } from 'react';
import { MasterMenu } from './ui/components/MasterMenu';
import { RefractionPanel } from './ui/components/RefractionPanel';
import { PrismPanel } from './ui/components/PrismPanel';
import { RaytracePanel } from './ui/components/RaytracePanel';
import { DropletPanel } from './ui/components/DropletPanel';
import type { SimulationId } from './app/registry';

function App() {
  const [activeId, setActiveId] = useState<SimulationId>('refraction');

  return (
    <div className="app-shell">
      <header className="hero">
        <p className="kicker">RainbowSim Web Overhaul</p>
        <h1>Physics Engines Separated From UI</h1>
        <p className="hero-copy">
          Component-by-component migration from pygame to web. Legacy desktop code in
          <code> src/rainbow_master</code> remains intact.
        </p>
      </header>

      <MasterMenu activeId={activeId} onPick={setActiveId} />

      <main className="workspace">
        {activeId === 'refraction' ? <RefractionPanel /> : null}
        {activeId === 'prism' ? <PrismPanel /> : null}
        {activeId === 'raytrace' ? <RaytracePanel /> : null}
        {activeId === 'droplet' ? <DropletPanel /> : null}
        {activeId !== 'refraction' && activeId !== 'prism' && activeId !== 'raytrace' && activeId !== 'droplet' ? (
          <section className="panel">
            <h2>Planned Component</h2>
            <p className="panel-lead">
              This module is queued for migration. We will port one component at a time
              into the shared architecture.
            </p>
          </section>
        ) : null}
      </main>
    </div>
  );
}

export default App;
