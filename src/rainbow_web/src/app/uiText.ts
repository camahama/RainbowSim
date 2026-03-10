import type { SimulationId } from './registry';

export const UI_TEXT = {
  appTitle: 'RainbowSim Presentation',
  appSubtitle: 'Select a module',
  menuButton: 'Menu',
  fallbackTitle: 'Module Unavailable',
  fallbackBody: 'This module is not available in the current build.',
  moduleButtons: {
    refraction: 'Refraction',
    prism: 'Prism',
    raytrace: 'Raytrace',
    droplet: 'Droplet',
    droplet2: 'Droplet 2',
    rainbow: 'Rainbow',
  } as Record<SimulationId, string>,
};
