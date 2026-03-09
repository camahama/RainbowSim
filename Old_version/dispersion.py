import pygame
import math
import sys

# --- Constants ---
WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 600
COLOR_BG = (10, 10, 20)
COLOR_WAVE = (100, 200, 255)
COLOR_ENVELOPE = (255, 100, 100)
COLOR_TEXT = (200, 200, 200)

# Physics
GRAVITY = 9.81
PI = math.pi

class WavePacketSim:
    def __init__(self):
        self.time = 0.0
        self.dt = 0.05
        
        # Wave Packet Parameters
        self.num_components = 100 # Number of sine waves to sum
        self.center_wavelength = 60.0 # Pixels
        self.packet_width_k = 0.02 # Width in k-space (inverse of spatial width)
        
        # Scaling
        self.amplitude_scale = 100.0
        self.y_offset = WINDOW_HEIGHT // 2
        
        # Precomputed components
        self.components = []
        self.recalculate_components()
        
        # Markers for tracking
        self.marker_x = 0.0

    def recalculate_components(self):
        self.components = []
        
        # Central wavenumber k0 = 2pi / lambda
        k0 = (2 * PI) / self.center_wavelength
        
        # Generate range of k values around k0
        # We want a Gaussian distribution of amplitudes
        
        # Range: +/- 3 standard deviations
        k_min = k0 - 3 * self.packet_width_k
        k_max = k0 + 3 * self.packet_width_k
        
        step = (k_max - k_min) / self.num_components
        
        for i in range(self.num_components):
            k = k_min + i * step
            
            # Avoid division by zero
            if k <= 0.0001: continue
            
            # Dispersion Relation for Deep Water: omega = sqrt(g * k)
            # (User asked for omega = sqrt(g/k) which is phase velocity, 
            # assuming deep water physics omega = sqrt(gk) here for realistic packet behavior)
            omega = math.sqrt(GRAVITY * k)
            
            # Gaussian Amplitude: exp(- (k-k0)^2 / (2*sigma^2) )
            amplitude = math.exp(-((k - k0)**2) / (2 * self.packet_width_k**2))
            
            # Normalize amplitude contribution
            amplitude /= self.num_components
            
            self.components.append({
                'k': k,
                'omega': omega,
                'amp': amplitude
            })

    def update(self):
        self.time += self.dt
        
        # Reset if packet moves off screen too far
        # Group velocity vg = 0.5 * sqrt(g/k)
        # Approx centroid calc
        k0 = (2 * PI) / self.center_wavelength
        vg = 0.5 * math.sqrt(GRAVITY / k0)
        packet_pos = vg * self.time * 20.0 # Scaling factor for pixel visualization
        
        if packet_pos > WINDOW_WIDTH + 400:
            self.time = 0.0

    def get_elevation(self, x):
        # Sum all cosine waves at position x
        y = 0.0
        
        # Scale x for physics context (pixels -> meters roughly)
        # Using a factor to make the motion visible on screen scale
        x_phys = x / 20.0 
        
        for c in self.components:
            # y = A * cos(kx - wt)
            phase = c['k'] * x_phys - c['omega'] * self.time
            y += c['amp'] * math.cos(phase)
            
        return y * self.amplitude_scale

    def get_envelope(self, x):
        # Theoretical envelope for visualization
        # Standard Gaussian propagation
        # A(x,t) ~ exp( - (x - vg*t)^2 / width )
        # Calculating this analytically is complex with dispersion spread.
        # We will instead compute the magnitude of the Hilbert transform approximation
        # or simply draw the summed wave and let the eye see the envelope.
        
        # Simple analytic approximation for non-dispersing Gaussian (just for tracking center)
        k0 = (2 * PI) / self.center_wavelength
        vg = 0.5 * math.sqrt(GRAVITY / k0)
        
        x_phys = x / 20.0
        center_pos = vg * self.time
        
        # Approximate spatial width (sigma_x = 1/sigma_k)
        sigma_x = 1.0 / self.packet_width_k
        
        dist = x_phys - center_pos
        env = math.exp(-(dist**2) / (2 * sigma_x**2))
        
        return env * self.amplitude_scale * 0.4 # Scaled down theoretical envelope

    def render(self, surface):
        # Draw center line
        pygame.draw.line(surface, (50, 50, 60), (0, self.y_offset), (WINDOW_WIDTH, self.y_offset))
        
        points = []
        # Optimization: Don't calculate every pixel, every 2nd is fine for smooth curves
        step = 2
        
        for x in range(0, WINDOW_WIDTH, step):
            y = self.get_elevation(x)
            points.append((x, self.y_offset - y))
            
        if len(points) > 1:
            pygame.draw.lines(surface, COLOR_WAVE, False, points, 2)

        # Optional: Draw theoretical group velocity tracker (Red vertical line)
        k0 = (2 * PI) / self.center_wavelength
        vg = 0.5 * math.sqrt(GRAVITY / k0)
        center_x_px = (vg * self.time) * 20.0
        
        # Draw Group Marker (Packet Center)
        if 0 < center_x_px < WINDOW_WIDTH:
            pygame.draw.line(surface, COLOR_ENVELOPE, (center_x_px, self.y_offset - 50), (center_x_px, self.y_offset + 50), 2)
            
        # Draw Phase Marker (Track one peak)
        # Phase velocity vp = sqrt(g/k) = 2 * vg
        # A specific peak moves at vp. 
        # x_peak = vp * t + phase_offset
        vp = math.sqrt(GRAVITY / k0)
        phase_x_px = ((vp * self.time) % (WINDOW_WIDTH/20 + 200)) * 20.0
        # This is just a visual guide moving at phase velocity
        # It won't perfectly track a specific crest as they appear/disappear, 
        # but shows the relative speed difference.
        
        # Better visual for Phase speed:
        # Draw a small dot that moves at phase speed at the top of the screen
        pygame.draw.circle(surface, COLOR_WAVE, (int(phase_x_px % WINDOW_WIDTH), self.y_offset - 120), 5)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Wave Packet: Phase vs Group Velocity")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16)
    
    sim = WavePacketSim()
    
    # UI Sliders
    slider_wl = pygame.Rect(150, 50, 200, 10)
    slider_width = pygame.Rect(150, 90, 200, 10)
    dragging_wl = False
    dragging_width = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if slider_wl.collidepoint(mx, my) or (abs(mx - slider_wl.centerx) < 110 and abs(my - slider_wl.centery) < 20):
                    dragging_wl = True
                elif slider_width.collidepoint(mx, my) or (abs(mx - slider_width.centerx) < 110 and abs(my - slider_width.centery) < 20):
                    dragging_width = True
                else:
                    # Click to reset time
                    sim.time = 0.0
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_wl = False
                dragging_width = False
                
            elif event.type == pygame.MOUSEMOTION:
                mx = event.pos[0]
                if dragging_wl:
                    ratio = (mx - slider_wl.x) / slider_wl.width
                    ratio = max(0.0, min(1.0, ratio))
                    # Wavelength 20 to 150
                    sim.center_wavelength = 20 + ratio * 130
                    sim.recalculate_components()
                if dragging_width:
                    ratio = (mx - slider_width.x) / slider_width.width
                    ratio = max(0.0, min(1.0, ratio))
                    # Width k: 0.005 (Wide packet) to 0.05 (Narrow packet)
                    sim.packet_width_k = 0.005 + ratio * 0.045
                    sim.recalculate_components()

        sim.update()
        
        screen.fill(COLOR_BG)
        sim.render(screen)
        
        # UI Rendering
        # 1. Wavelength
        pygame.draw.rect(screen, (80, 80, 80), slider_wl, border_radius=5)
        ratio_wl = (sim.center_wavelength - 20) / 130
        kx = slider_wl.x + ratio_wl * slider_wl.width
        pygame.draw.circle(screen, (200, 200, 200), (int(kx), slider_wl.centery), 8)
        lbl1 = font.render(f"Wavelength (k0): {int(sim.center_wavelength)}", True, COLOR_TEXT)
        screen.blit(lbl1, (slider_wl.right + 15, slider_wl.y - 10))
        
        # 2. Packet Width
        pygame.draw.rect(screen, (80, 80, 80), slider_width, border_radius=5)
        ratio_w = (sim.packet_width_k - 0.005) / 0.045
        kx = slider_width.x + ratio_w * slider_width.width
        pygame.draw.circle(screen, (200, 200, 200), (int(kx), slider_width.centery), 8)
        lbl2 = font.render(f"Packet Compactness (Delta k)", True, COLOR_TEXT)
        screen.blit(lbl2, (slider_width.right + 15, slider_width.y - 10))
        
        # Legend
        leg_x = 50
        leg_y = WINDOW_HEIGHT - 100
        pygame.draw.circle(screen, COLOR_WAVE, (leg_x, leg_y), 5)
        screen.blit(font.render("Phase Velocity (Individual Waves) - Blue Dot", True, COLOR_WAVE), (leg_x + 15, leg_y - 10))
        
        pygame.draw.line(screen, COLOR_ENVELOPE, (leg_x - 5, leg_y + 30), (leg_x + 5, leg_y + 30), 2)
        screen.blit(font.render("Group Velocity (The Packet) - Red Line", True, COLOR_ENVELOPE), (leg_x + 15, leg_y + 20))
        
        info = font.render("Observation: Ripples appear at the back, move through, and die at the front.", True, (150, 150, 150))
        screen.blit(info, (WINDOW_WIDTH//2 - info.get_width()//2, WINDOW_HEIGHT - 40))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()