export type SimulationId = 'refraction' | 'prism' | 'raytrace' | 'droplet' | 'droplet2' | 'rainbow';

export type SimulationMeta = {
  id: SimulationId;
  title: string;
  subtitle: string;
  status: 'ready' | 'planned';
};

export const SIMULATIONS: SimulationMeta[] = [
  {
    id: 'refraction',
    title: 'Refraction Lab',
    subtitle: 'Snell, critical angle, and Fresnel estimate',
    status: 'ready',
  },
  {
    id: 'prism',
    title: 'Prism',
    subtitle: 'Dispersion through triangular medium',
    status: 'ready',
  },
  {
    id: 'raytrace',
    title: 'Raytrace',
    subtitle: 'Geometric ray path visualizer',
    status: 'ready',
  },
  {
    id: 'droplet',
    title: 'Droplet',
    subtitle: 'Two-bounce rain droplet model',
    status: 'ready',
  },
  {
    id: 'droplet2',
    title: 'Droplet 2',
    subtitle: 'Realistic droplet profile and highlights',
    status: 'ready',
  },
  {
    id: 'rainbow',
    title: 'Rainbow Field',
    subtitle: 'Observer-angle color accumulation',
    status: 'planned',
  },
];
