import pygame
import math
import sys

# --- Constants ---
WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 700
GRID_WIDTH, GRID_HEIGHT = 800, 500 
CELL_SIZE = WINDOW_WIDTH // GRID_WIDTH

# Physics
# Återställt till höga värden för att undvika "blobb-effekten"
DAMPING = 0.995 
WAVE_SPEED = 0.5 

# Colors
COLOR_BG = (10, 10, 10)
COLOR_UI_BG = (30, 30, 30)
COLOR_TEXT = (200, 200, 200)
COLOR_WALL = (100, 100, 100)

def wavelength_to_rgb(wavelength):
    """Converts a wavelength (nm) to an RGB color tuple."""
    gamma = 0.8
    intensity_max = 255
    factor = 0.0
    R, G, B = 0, 0, 0

    if 380 <= wavelength < 440:
        R = -(wavelength - 440) / (440 - 380); G = 0.0; B = 1.0
    elif 440 <= wavelength < 490:
        R = 0.0; G = (wavelength - 440) / (490 - 440); B = 1.0
    elif 490 <= wavelength < 510:
        R = 0.0; G = 1.0; B = -(wavelength - 510) / (510 - 490)
    elif 510 <= wavelength < 580:
        R = (wavelength - 510) / (580 - 510); G = 1.0; B = 0.0
    elif 580 <= wavelength < 645:
        R = 1.0; G = -(wavelength - 645) / (645 - 580); B = 0.0
    elif 645 <= wavelength <= 750:
        R = 1.0; G = 0.0; B = 0.0

    if 380 <= wavelength < 420:
        factor = 0.3 + 0.7 * (wavelength - 380) / (420 - 380)
    elif 420 <= wavelength < 700:
        factor = 1.0
    elif 700 <= wavelength <= 750:
        factor = 0.3 + 0.7 * (750 - wavelength) / (750 - 700)

    rgb = []
    for c in [R, G, B]:
        val = int(intensity_max * (c * factor) ** gamma)
        rgb.append(val)
    return tuple(rgb)

class WaveSimulation:
    def __init__(self):
        self.width = GRID_WIDTH
        self.height = GRID_HEIGHT
        
        self.size = self.width * self.height
        self.buffer1 = [0.0] * self.size
        self.buffer2 = [0.0] * self.size
        
        self.obstacles = [False] * self.size
        self.damping_map = [DAMPING] * self.size
        
        self.create_geometry()
        
        self.wavelength_nm = 550 
        self.phase = 0.0 
        
    def create_geometry(self):
        # Marginal för dämpzoner vid kanterna
        margin = 30 
        
        # Geometri för bollen
        cx = self.width // 3
        cy = self.height // 2
        radius = 20 
        r_sq = radius * radius
        
        for y in range(self.height):
            for x in range(self.width):
                idx = y * self.width + x
                
                # --- 1. Absorbing Boundaries (Sponge) ---
                dist_left = x
                dist_right = self.width - 1 - x
                dist_top = y
                dist_bottom = self.height - 1 - y
                
                min_dist = min(dist_left, dist_right, dist_top, dist_bottom)
                
                if min_dist < margin:
                    factor = (min_dist / margin) ** 2
                    # Mjuk absorption vid kanterna
                    self.damping_map[idx] = 0.5 + 0.5 * factor

                # --- 2. Absorbing Ball ---
                if (x - cx)**2 + (y - cy)**2 <= r_sq:
                    # Absorberande boll (Dämpning = 0 dödar vågen helt)
                    self.damping_map[idx] = 0.0 
                    # Vi sätter inte obstacles=True, för vi vill att vågen ska gå in och dö, inte studsa.

    def _build_geometry_round_obstacle(self):
        # Denna funktion behövs inte längre då logiken ligger i create_geometry, 
        # men vi behåller namnet för kompatibilitet om det anropas externt.
        pass 

    def get_frequency_from_wavelength(self):
        # Justerad för WAVE_SPEED 0.5
        target_lambda_px = 20.0
        omega = 2 * math.pi * WAVE_SPEED / target_lambda_px
        return omega

    def update(self):
        w = self.width
        h = self.height
        b1 = self.buffer1 
        b2 = self.buffer2 
        obs = self.obstacles
        damp = self.damping_map
        
        # Wave Equation Solver
        for y in range(1, h - 1):
            row_offset = y * w
            for x in range(1, w - 1):
                idx = row_offset + x
                
                if obs[idx]:
                    b2[idx] = 0
                    continue
                
                val = (b1[idx + 1] + 
                       b1[idx - 1] + 
                       b1[idx + w] + 
                       b1[idx - w]) / 2.0 - b1[idx]
                
                new_val = val * WAVE_SPEED + 2 * b1[idx] - b2[idx]
                new_val *= damp[idx]
                
                b2[idx] = new_val

        # --- Soft Source Injection ---
        freq = self.get_frequency_from_wavelength()
        self.phase += freq
        source_force = math.sin(self.phase) * 50.0 
        
        source_x = 40 
        for y in range(20, h - 20):
            idx = y * w + source_x
            if not obs[idx]:
                b2[idx] += source_force

        # Swap buffers
        self.buffer1, self.buffer2 = self.buffer2, self.buffer1

    def render(self, surface, current_color):
        pixel_array = pygame.PixelArray(surface)
        w = self.width
        h = self.height
        base_r, base_g, base_b = current_color
        
        for y in range(h):
            row_offset = y * w
            for x in range(w):
                idx = row_offset + x
                
                # Visa hinder/absorberande objekt
                if self.damping_map[idx] == 0.0:
                    pixel_array[x, y] = (20, 20, 20)
                elif self.obstacles[idx]:
                    pixel_array[x, y] = COLOR_WALL
                else:
                    val = self.buffer1[idx]
                    
                    # Visa endast positiva toppar (Högkontrast)
                    intensity = max(0, min(255, int(val)))
                    
                    r = (base_r * intensity) // 255
                    g = (base_g * intensity) // 255
                    b = (base_b * intensity) // 255
                    
                    pixel_array[x, y] = (r, g, b)
                    
        pixel_array.close()

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Wave Simulation: Diffraction")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)
    
    sim = WaveSimulation()
    
    sim_surface = pygame.Surface((GRID_WIDTH, GRID_HEIGHT))
    
    slider_rect = pygame.Rect(100, WINDOW_HEIGHT - 60, WINDOW_WIDTH - 200, 10)
    slider_knob_rad = 10
    dragging = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                progress = (sim.wavelength_nm - 400) / (700 - 400)
                knob_x = slider_rect.x + int(progress * slider_rect.width)
                knob_rect = pygame.Rect(knob_x - 15, slider_rect.y - 15, 30, 30)
                
                if knob_rect.collidepoint(mx, my):
                    dragging = True
                elif slider_rect.collidepoint(mx, my):
                    dragging = True
            
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
                
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    mx = event.pos[0]
                    mx = max(slider_rect.left, min(slider_rect.right, mx))
                    ratio = (mx - slider_rect.left) / slider_rect.width
                    new_nm = 400 + ratio * (300)
                    sim.wavelength_nm = new_nm

        sim.update()
        current_rgb = wavelength_to_rgb(sim.wavelength_nm)
        sim.render(sim_surface, current_rgb)
        
        scaled_surf = pygame.transform.scale(sim_surface, (WINDOW_WIDTH, WINDOW_HEIGHT - 100))
        screen.fill(COLOR_BG)
        screen.blit(scaled_surf, (0, 0))
        
        pygame.draw.rect(screen, COLOR_UI_BG, (0, WINDOW_HEIGHT - 100, WINDOW_WIDTH, 100))
        pygame.draw.rect(screen, (100, 100, 100), slider_rect, border_radius=5)
        
        for i in range(slider_rect.width):
            nm_grad = 400 + (i / slider_rect.width) * 300
            col_grad = wavelength_to_rgb(nm_grad)
            pygame.draw.line(screen, col_grad, (slider_rect.x + i, slider_rect.y), (slider_rect.x + i, slider_rect.bottom))
            
        progress = (sim.wavelength_nm - 400) / 300
        knob_x = slider_rect.x + int(progress * slider_rect.width)
        pygame.draw.circle(screen, (255, 255, 255), (knob_x, slider_rect.centery), 12)
        pygame.draw.circle(screen, current_rgb, (knob_x, slider_rect.centery), 9)
        
        lbl_val = font.render(f"Färg (Våglängd): {int(sim.wavelength_nm)} nm", True, current_rgb)
        screen.blit(lbl_val, (WINDOW_WIDTH//2 - lbl_val.get_width()//2, slider_rect.y - 30))
        
        lbl_400 = font.render("400 nm", True, (150, 150, 150))
        screen.blit(lbl_400, (slider_rect.left, slider_rect.bottom + 10))
        
        lbl_700 = font.render("700 nm", True, (150, 150, 150))
        screen.blit(lbl_700, (slider_rect.right - lbl_700.get_width(), slider_rect.bottom + 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()