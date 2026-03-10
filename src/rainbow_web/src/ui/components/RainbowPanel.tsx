import { useEffect, useRef, useState } from 'react';
import { RainbowSimulation, type RainbowDropSample } from '../../simulations/rainbow/rainbowSimulation';
import { UI_TEXT } from '../../app/uiText';
import { UI_PARAMS } from '../../app/uiParams';

const sim = new RainbowSimulation();
const W = UI_PARAMS.rainbow.canvasWidth;
const H = UI_PARAMS.rainbow.canvasHeight;

function drawBackground(ctx: CanvasRenderingContext2D): void {
  const sky = ctx.createLinearGradient(0, 0, 0, H * 0.62);
  sky.addColorStop(0, '#2c5f87');
  sky.addColorStop(0.45, '#5d90b4');
  sky.addColorStop(1, '#a4c0cf');
  ctx.fillStyle = sky;
  ctx.fillRect(0, 0, W, H);

  const ground = ctx.createLinearGradient(0, H * 0.55, 0, H);
  ground.addColorStop(0, '#49643f');
  ground.addColorStop(1, '#273823');
  ctx.fillStyle = ground;
  ctx.fillRect(0, H * 0.55, W, H * 0.45);
}

function drawBackgroundFromImage(ctx: CanvasRenderingContext2D, img: HTMLImageElement | null): void {
  if (img && img.complete && img.naturalWidth > 0) {
    ctx.drawImage(img, 0, 0, W, H);
    return;
  }
  drawBackground(ctx);
}

type LayerState = {
  canvas: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;
  imageData: ImageData;
  pixels: Uint8ClampedArray;
  dirty: boolean;
};

function stampToLayer(layer: LayerState, drop: RainbowDropSample): void {
  if (drop.intensity <= 0.001) {
    return;
  }

  const chroma = Math.max(drop.r, drop.g, drop.b);
  if (chroma <= 0) {
    return;
  }

  const minX = Math.max(0, Math.floor(drop.x - drop.radius));
  const maxX = Math.min(W - 1, Math.ceil(drop.x + drop.radius));
  const minY = Math.max(0, Math.floor(drop.y - drop.radius));
  const maxY = Math.min(H - 1, Math.ceil(drop.y + drop.radius));

  for (let yy = minY; yy <= maxY; yy += 1) {
    for (let xx = minX; xx <= maxX; xx += 1) {
      const dx = xx + 0.5 - drop.x;
      const dy = yy + 0.5 - drop.y;
      const dist = Math.hypot(dx, dy);
      if (dist > drop.radius) {
        continue;
      }

      const t = dist / Math.max(1e-6, drop.radius);
      const iLift = Math.pow(Math.max(0, Math.min(1, drop.intensity)), 0.72);
      const iTone = iLift / (1 + 0.55 * iLift);
      const a = iTone * (1 - t) * (1 - t);
      if (a <= 0.001) {
        continue;
      }

      const alpha = Math.max(0, Math.min(255, Math.floor(a * 255)));
      const idx = (yy * W + xx) * 4;

      // Non-additive compositing: keep the strongest droplet contribution only.
      if (alpha <= layer.pixels[idx + 3]) {
        continue;
      }

      layer.pixels[idx] = drop.r;
      layer.pixels[idx + 1] = drop.g;
      layer.pixels[idx + 2] = drop.b;
      layer.pixels[idx + 3] = alpha;
      layer.dirty = true;
    }
  }
}

function previewFillColor(r: number, g: number, b: number, intensity: number): string {
  if (intensity <= 0.001) {
    return 'rgb(0,0,0)';
  }

  const iLift = Math.pow(Math.max(0, Math.min(1, intensity)), 0.72);
  const k = iLift / (1 + 0.55 * iLift);
  const rr = Math.max(0, Math.min(255, Math.floor(r * k)));
  const gg = Math.max(0, Math.min(255, Math.floor(g * k)));
  const bb = Math.max(0, Math.min(255, Math.floor(b * k)));
  return `rgb(${rr}, ${gg}, ${bb})`;
}

export function RainbowPanel() {
  const text = UI_TEXT.modules.rainbow;
  const [ui, setUi] = useState(sim.uiState());
  const [isDragging, setIsDragging] = useState(false);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const layerRef = useRef<LayerState | null>(null);
  const draggingRef = useRef(false);
  const previewRef = useRef<{ x: number; y: number } | null>(null);
  const bgImageRef = useRef<HTMLImageElement | null>(null);

  useEffect(() => {
    const layer = document.createElement('canvas');
    layer.width = W;
    layer.height = H;
    const lctx = layer.getContext('2d');
    if (!lctx) {
      return undefined;
    }

    const imageData = lctx.createImageData(W, H);
    layerRef.current = {
      canvas: layer,
      ctx: lctx,
      imageData,
      pixels: imageData.data,
      dirty: false,
    };

    const img = new Image();
    img.src = `${import.meta.env.BASE_URL}landscape.jpg`;
    img.onload = () => {
      bgImageRef.current = img;
    };
    img.onerror = () => {
      bgImageRef.current = null;
    };

    const raf = { id: 0 };
    let lastUi = 0;

    const draw = (ts: number) => {
      const rain = sim.rainTick();
      const layerState = layerRef.current;
      if (layerState) {
        for (const d of rain) {
          stampToLayer(layerState, d);
        }
        if (layerState.dirty) {
          layerState.ctx.putImageData(layerState.imageData, 0, 0);
          layerState.dirty = false;
        }
      }

      const canvas = canvasRef.current;
      const ctx = canvas?.getContext('2d');
      if (ctx && layerState) {
        drawBackgroundFromImage(ctx, bgImageRef.current);
        ctx.drawImage(layerState.canvas, 0, 0);

        const preview = previewRef.current;
        if (preview) {
          const p = sim.previewDrop(preview.x, preview.y);
          const col = previewFillColor(p.r, p.g, p.b, Math.min(1, p.intensity * 2));
          ctx.strokeStyle = 'rgba(255,255,255,0.85)';
          ctx.lineWidth = 1.2;
          ctx.fillStyle = col;
          ctx.beginPath();
          ctx.arc(preview.x, preview.y, 8, 0, Math.PI * 2);
          ctx.fill();
          ctx.stroke();
        }
      }

      if (ts - lastUi > 120) {
        lastUi = ts;
        setUi(sim.uiState());
      }

      raf.id = window.requestAnimationFrame(draw);
    };

    raf.id = window.requestAnimationFrame(draw);
    return () => window.cancelAnimationFrame(raf.id);
  }, []);

  const mapToScene = (evt: React.PointerEvent<HTMLCanvasElement>) => {
    const rect = evt.currentTarget.getBoundingClientRect();
    const sx = W / rect.width;
    const sy = H / rect.height;
    return {
      x: (evt.clientX - rect.left) * sx,
      y: (evt.clientY - rect.top) * sy,
    };
  };

  const drawManual = (x: number, y: number, boost: boolean) => {
    const d = sim.manualDrop(x, y, boost);
    const layerState = layerRef.current;
    if (d && layerState) {
      stampToLayer(layerState, d);
      if (layerState.dirty) {
        layerState.ctx.putImageData(layerState.imageData, 0, 0);
        layerState.dirty = false;
      }
      setUi(sim.uiState());
    }
  };

  return (
    <section className="panel">
      <h2>{text.title}</h2>
      <p className="panel-lead">{text.lead}</p>

      <div className="controls">
        <div className="mode-row">
          <button
            type="button"
            className={ui.simulating ? 'mode-btn active' : 'mode-btn'}
            onClick={() => {
              sim.toggleSimulating();
              setUi(sim.uiState());
            }}
          >
            {ui.simulating ? text.stopRain : text.startRain}
          </button>
          <button
            type="button"
            className="mode-btn"
            onClick={() => {
              sim.clear();
              const layerState = layerRef.current;
              if (layerState) {
                layerState.pixels.fill(0);
                layerState.ctx.putImageData(layerState.imageData, 0, 0);
                layerState.dirty = false;
              }
              setUi(sim.uiState());
            }}
          >
            {text.clear}
          </button>
        </div>
      </div>

      <div className="prism-canvas-wrap">
        <canvas
          ref={canvasRef}
          className={isDragging ? 'prism-canvas drag-hidden-cursor' : 'prism-canvas'}
          width={W}
          height={H}
          onPointerDown={(e) => {
            draggingRef.current = true;
            setIsDragging(true);
            const p = mapToScene(e);
            previewRef.current = p;
          }}
          onPointerMove={(e) => {
            if (!draggingRef.current) {
              return;
            }
            const p = mapToScene(e);
            previewRef.current = p;
          }}
          onPointerUp={() => {
            const p = previewRef.current;
            if (draggingRef.current && p) {
              drawManual(p.x, p.y, false);
            }
            draggingRef.current = false;
            setIsDragging(false);
            previewRef.current = null;
          }}
          onPointerLeave={() => {
            if (draggingRef.current && previewRef.current) {
              const p = previewRef.current;
              drawManual(p.x, p.y, false);
            }
            draggingRef.current = false;
            setIsDragging(false);
            previewRef.current = null;
          }}
          aria-label="Rainbow field accumulation"
        />
      </div>

      <div className="stats">
        <div>
          <span>{text.drops}</span>
          <strong>{ui.totalPoints.toLocaleString()}</strong>
        </div>
        <div>
          <span>{text.rate}</span>
          <strong>{ui.simulating ? Math.floor(ui.pointsPerFrame) : 0}{text.frameSuffix}</strong>
        </div>
        <div>
          <span>{text.manualInput}</span>
          <strong>{text.manualHint}</strong>
        </div>
      </div>
    </section>
  );
}
