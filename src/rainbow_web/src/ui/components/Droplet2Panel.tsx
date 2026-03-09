import { useEffect, useRef, useState } from 'react';
import { DROPLET2_BANDS } from '../../physics/droplet2/engine';
import { Droplet2Simulation } from '../../simulations/droplet2/droplet2Simulation';

const sim = new Droplet2Simulation();

const SCENE_W = 1000;
const SCENE_H = 560;

function clearCanvas(ctx: CanvasRenderingContext2D | null): void {
  if (!ctx) {
    return;
  }
  ctx.clearRect(0, 0, SCENE_W, SCENE_H);
}

function drawRay(
  ctx: CanvasRenderingContext2D,
  points: { x: number; y: number }[],
  stroke: string,
  width: number,
  alpha: number,
): void {
  if (points.length < 2) {
    return;
  }
  ctx.globalAlpha = alpha;
  ctx.strokeStyle = stroke;
  ctx.lineWidth = width;
  ctx.beginPath();
  ctx.moveTo(points[0].x, points[0].y);
  for (let i = 1; i < points.length; i += 1) {
    ctx.lineTo(points[i].x, points[i].y);
  }
  ctx.stroke();
  ctx.globalAlpha = 1;
}

export function Droplet2Panel() {
  const [ui, setUi] = useState(sim.uiState());

  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const pTransRef = useRef<CanvasRenderingContext2D | null>(null);
  const pReflRef = useRef<CanvasRenderingContext2D | null>(null);
  const sTransRef = useRef<CanvasRenderingContext2D | null>(null);
  const sReflRef = useRef<CanvasRenderingContext2D | null>(null);

  const pTransLen = useRef(0);
  const pReflLen = useRef(0);
  const sTransLen = useRef(0);
  const sReflLen = useRef(0);

  const lastUiUpdate = useRef(0);

  useEffect(() => {
    function makeLayerCtx(): CanvasRenderingContext2D | null {
      const layer = document.createElement('canvas');
      layer.width = SCENE_W;
      layer.height = SCENE_H;
      return layer.getContext('2d');
    }

    pTransRef.current = makeLayerCtx();
    pReflRef.current = makeLayerCtx();
    sTransRef.current = makeLayerCtx();
    sReflRef.current = makeLayerCtx();

    const raf = { id: 0 };

    const drawFrame = (ts: number) => {
      sim.tick();
      const frame = sim.frameState();

      const pTrans = pTransRef.current;
      const pRefl = pReflRef.current;
      const sTrans = sTransRef.current;
      const sRefl = sReflRef.current;

      if (pTrans && pRefl && sTrans && sRefl) {
        for (let i = pTransLen.current; i < frame.primaryTransmittedRays.length; i += 1) {
          drawRay(pTrans, frame.primaryTransmittedRays[i].points, 'rgb(245,245,235)', 0.9, 0.045);
        }
        pTransLen.current = frame.primaryTransmittedRays.length;

        for (let i = pReflLen.current; i < frame.primaryRays.length; i += 1) {
          const ray = frame.primaryRays[i];
          drawRay(pRefl, ray.points, DROPLET2_BANDS[ray.bandIndex].hex, 1.1, 0.14);
        }
        pReflLen.current = frame.primaryRays.length;

        for (let i = sTransLen.current; i < frame.secondaryTransmittedRays.length; i += 1) {
          drawRay(sTrans, frame.secondaryTransmittedRays[i].points, 'rgb(245,245,235)', 0.9, 0.045);
        }
        sTransLen.current = frame.secondaryTransmittedRays.length;

        for (let i = sReflLen.current; i < frame.secondaryRays.length; i += 1) {
          const ray = frame.secondaryRays[i];
          drawRay(sRefl, ray.points, DROPLET2_BANDS[ray.bandIndex].hex, 1.25, 0.12);
        }
        sReflLen.current = frame.secondaryRays.length;
      }

      const canvas = canvasRef.current;
      const ctx = canvas?.getContext('2d');
      if (ctx) {
        ctx.globalCompositeOperation = 'source-over';
        ctx.clearRect(0, 0, SCENE_W, SCENE_H);
        ctx.fillStyle = '#07090d';
        ctx.fillRect(0, 0, SCENE_W, SCENE_H);

        ctx.beginPath();
        ctx.arc(frame.center.x, frame.center.y, frame.radius, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(35, 44, 96, 0.45)';
        ctx.fill();
        ctx.strokeStyle = 'rgba(220, 228, 250, 0.9)';
        ctx.lineWidth = 1.8;
        ctx.stroke();

        ctx.globalCompositeOperation = 'screen';
        if (frame.primaryVisible && pTransRef.current && pReflRef.current) {
          ctx.drawImage((pTransRef.current.canvas), 0, 0);
          ctx.drawImage((pReflRef.current.canvas), 0, 0);
        }
        if (frame.secondaryVisible && sTransRef.current && sReflRef.current) {
          ctx.drawImage((sTransRef.current.canvas), 0, 0);
          ctx.drawImage((sReflRef.current.canvas), 0, 0);
        }
        ctx.globalCompositeOperation = 'source-over';
      }

      if (ts - lastUiUpdate.current > 80) {
        lastUiUpdate.current = ts;
        setUi(sim.uiState());
      }

      raf.id = window.requestAnimationFrame(drawFrame);
    };

    raf.id = window.requestAnimationFrame(drawFrame);

    return () => window.cancelAnimationFrame(raf.id);
  }, []);

  const primaryLabel = ui.primaryVisible ? 'Primary: CLEAR' : 'Primary: START';
  const secondaryLabel = ui.secondaryVisible ? 'Secondary: CLEAR' : 'Secondary: START';
  const showTransmission = ui.primaryVisible || ui.secondaryVisible;
  const progress = `${ui.primaryCursor} / ${ui.secondaryCursor}`;

  const resetPrimaryLayer = () => {
    clearCanvas(pTransRef.current);
    clearCanvas(pReflRef.current);
    pTransLen.current = 0;
    pReflLen.current = 0;
  };

  const resetSecondaryLayer = () => {
    clearCanvas(sTransRef.current);
    clearCanvas(sReflRef.current);
    sTransLen.current = 0;
    sReflLen.current = 0;
  };

  const resetAllLayers = () => {
    resetPrimaryLayer();
    resetSecondaryLayer();
  };

  return (
    <section className="panel">
      <h2>Droplet 2 Lab</h2>
      <p className="panel-lead">Animated accumulation layers inspired by the legacy advanced droplet view.</p>

      <div className="controls">
        <div className="mode-row" role="group" aria-label="Droplet2 controls">
          <button
            type="button"
            className={ui.primaryVisible ? 'mode-btn active' : 'mode-btn'}
            onClick={() => {
              const live = sim.getState();
              if (live.primaryVisible) {
                sim.clearPrimary();
                resetPrimaryLayer();
              } else {
                sim.startPrimary();
                resetPrimaryLayer();
              }
              setUi(sim.uiState());
            }}
          >
            {primaryLabel}
          </button>
          <button
            type="button"
            className={ui.secondaryVisible ? 'mode-btn active' : 'mode-btn'}
            onClick={() => {
              const live = sim.getState();
              if (live.secondaryVisible) {
                sim.clearSecondary();
                resetSecondaryLayer();
              } else {
                sim.startSecondary();
                resetSecondaryLayer();
              }
              setUi(sim.uiState());
            }}
          >
            {secondaryLabel}
          </button>
        </div>

        <label>
          Droplet radius: <strong>{ui.radius.toFixed(0)} px</strong>
          <input
            type="range"
            min={10}
            max={60}
            step={1}
            value={ui.radius}
            onChange={(e) => {
              sim.setRadius(Number(e.target.value));
              resetAllLayers();
              setUi(sim.uiState());
            }}
          />
        </label>

        <label>
          Sweep speed: <strong>{ui.raysPerTick}</strong>
          <input
            type="range"
            min={1}
            max={4}
            step={1}
            value={ui.raysPerTick}
            onChange={(e) => {
              sim.setRaysPerTick(Number(e.target.value));
              setUi(sim.uiState());
            }}
          />
        </label>
      </div>

      <div className="prism-canvas-wrap">
        <canvas
          ref={canvasRef}
          className="prism-canvas"
          width={SCENE_W}
          height={SCENE_H}
          aria-label="Animated droplet accumulation"
        />
      </div>

      <div className="stats">
        <div>
          <span>Primary status</span>
          <strong>{ui.primaryAnimating ? 'Animating' : ui.primaryVisible ? 'Complete' : 'Off'}</strong>
        </div>
        <div>
          <span>Secondary status</span>
          <strong>{ui.secondaryAnimating ? 'Animating' : ui.secondaryVisible ? 'Complete' : 'Off'}</strong>
        </div>
        <div>
          <span>Cursors (P/S)</span>
          <strong>{progress}</strong>
        </div>
        <div>
          <span>Transmission cue</span>
          <strong>{showTransmission ? 'Direct refracted bundle shown' : 'Off (start primary/secondary)'}</strong>
        </div>
      </div>
    </section>
  );
}
