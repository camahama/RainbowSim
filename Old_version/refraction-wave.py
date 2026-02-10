import pygame
import math
import sys

# --- Constants ---
WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 700
# Vi minskar upplösningen till 300x175 för att kunna köra fler fysiksteg per sekund
GRID_WIDTH, GRID_HEIGHT = 600, 350 
CELL_SIZE = WINDOW_WIDTH // GRID_WIDTH

# Physics
BASE_WAVE_SPEED = 0.5  # Hastighet i vakuum (luft)
DAMPING = 0.995        # Bevara energi men döda evighets-eko

# Colors
COLOR_BG = (0, 0, 0)
COLOR_UI_BG = (30, 30, 30)
COLOR_GLASS = (20, 20, 40) # Svag blåton för glaset

def wavelength_to_rgb(wavelength):
    # Vi kör en fast grön färg för tydlighet i denna demo,
    # men behåller funktionen om vi vill byta.
    return (0, 255, 100)

class WaveSolver:
    def __init__(self):
        self.width = GRID_WIDTH
        self.height = GRID_HEIGHT
        self.size = self.width * self.height
        
        # Buffertar
        self.u = [0.0] * self.size
        self.u_prev = [0.0] * self.size
        self.u_next = [0.0] * self.size
        
        # Kartor
        self.speed_map = [1.0] * self.size
        self.damping_map = [1.0] * self.size
        self.glass_mask = [False] * self.size # För visualisering
        
        # Inställningar
        self.refractive_index = 2.0 # Startvärde (Glas)
        self.phase = 0.0
        self.frequency = 0.15 # Halverad frekvens för dubbel våglängd
        
        self.build_geometry()

    def build_geometry(self):
        """Bygger upp mediet: Luft (vänster) och Glas (höger) med en sned gräns."""
        margin = 15 # Mindre marginal för lägre upplösning
        
        # Ekvation för gränslinjen (x = ky + m)
        # Vi lutar den så toppen är längre högerut än botten
        slope = 0.4 
        offset = self.width // 2 - 25
        
        current_inv_n = 1.0 / self.refractive_index
        
        for y in range(self.height):
            # X-koordinat där glaset börjar på denna rad
            boundary_x = int(slope * (y - self.height/2) + offset)
            
            for x in range(self.width):
                idx = y * self.width + x
                
                # --- 1. Material (Hastighet) ---
                if x > boundary_x:
                    # Inne i glaset: Lägre hastighet
                    self.speed_map[idx] = current_inv_n
                    self.glass_mask[idx] = True
                else:
                    # I luften: Full hastighet
                    self.speed_map[idx] = 1.0
                    self.glass_mask[idx] = False
                
                # --- 2. Dämpning (Sponge Layer) ---
                # Absorbera vid kanterna för att undvika reflektioner
                dist_left = x
                dist_right = self.width - 1 - x
                dist_top = y
                dist_bottom = self.height - 1 - y
                min_dist = min(dist_left, dist_right, dist_top, dist_bottom)
                
                if min_dist < margin:
                    factor = (min_dist / margin) ** 2
                    self.damping_map[idx] = 0.6 + 0.395 * factor
                else:
                    self.damping_map[idx] = DAMPING

    def set_refractive_index(self, n):
        if abs(self.refractive_index - n) > 0.01:
            self.refractive_index = n
            self.build_geometry() # Bygg om hastighetskartan

    def update(self):
        w = self.width
        h = self.height
        
        # Referenser
        u = self.u
        u_old = self.u_prev
        u_new = self.u_next
        speed_map = self.speed_map
        damp = self.damping_map
        
        base_c2 = BASE_WAVE_SPEED * BASE_WAVE_SPEED
        
        # --- Wave Equation (FDTD) ---
        for y in range(1, h - 1):
            row_offset = y * w
            for x in range(1, w - 1):
                i = row_offset + x
                
                # Laplacian
                laplacian = (u[i-1] + u[i+1] + u[i-w] + u[i+w] - 4*u[i])
                
                # Lokal hastighet i kvadrat: c^2 = (base_c * map_val)^2
                local_c2 = base_c2 * (speed_map[i] ** 2)
                
                # Integration
                val = 2*u[i] - u_old[i] + local_c2 * laplacian
                
                u_new[i] = val * damp[i]

        # --- Plane Wave Source ---
        # En linje-källa en bit in från vänsterkanten
        self.phase += self.frequency
        source_val = math.sin(self.phase) * 5.0 # Mjukare amplitud
        
        source_x = 20 # Anpassat för lägre upplösning
        
        # Halverad bredd: Använd mitten-halvan av höjden
        margin_y = h // 4
        
        for y in range(margin_y, h - margin_y):
            idx = y * w + source_x
            # Additiv källa ("Soft Source") låter reflektioner passera igenom
            u_new[idx] += source_val

        # Swap buffers
        self.u_prev = u
        self.u = u_new
        self.u_next = u_old

    def render(self, surface):
        pixels = pygame.PixelArray(surface)
        w = self.width
        h = self.height
        
        green_base = (0, 255, 100)
        
        for y in range(h):
            row_offset = y * w
            for x in range(w):
                idx = row_offset + x
                
                # Bakgrund: Rita glaset svagt blått
                if self.glass_mask[idx]:
                    bg_col = COLOR_GLASS
                else:
                    bg_col = COLOR_BG
                
                val = self.u[idx]
                
                # Visualisering: Visa positiva toppar som Grönt
                intensity = max(0, min(255, int(val * 10))) # Skala upp för synlighet
                
                if intensity > 5:
                    # Additiv blandning av vågtopp + bakgrund
                    r = min(255, bg_col[0] + 0)
                    g = min(255, bg_col[1] + intensity)
                    b = min(255, bg_col[2] + intensity // 2)
                    pixels[x, y] = (r, g, b)
                else:
                    pixels[x, y] = bg_col
                    
        pixels.close()

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Wave Refraction: Snell's Law in Action")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)
    
    sim = WaveSolver()
    sim_surface = pygame.Surface((GRID_WIDTH, GRID_HEIGHT))
    
    # Slider
    slider_rect = pygame.Rect(200, WINDOW_HEIGHT - 60, WINDOW_WIDTH - 400, 10)
    dragging = False
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if slider_rect.collidepoint(mx, my) or abs(my - slider_rect.centery) < 20:
                    if slider_rect.left <= mx <= slider_rect.right:
                        dragging = True
            
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
                
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    mx = event.pos[0]
                    mx = max(slider_rect.left, min(slider_rect.right, mx))
                    ratio = (mx - slider_rect.left) / slider_rect.width
                    # Index range: 1.0 to 3.0
                    new_n = 1.0 + ratio * 2.0
                    sim.set_refractive_index(new_n)

        # Update & Render
        # Kör fysiken 4 gånger per bildruta för snabbare propagering
        for _ in range(4):
            sim.update()
            
        sim.render(sim_surface)
        
        # Scale up
        scaled_surf = pygame.transform.scale(sim_surface, (WINDOW_WIDTH, WINDOW_HEIGHT - 100))
        screen.fill(COLOR_BG)
        screen.blit(scaled_surf, (0, 0))
        
        # UI
        pygame.draw.rect(screen, COLOR_UI_BG, (0, WINDOW_HEIGHT - 100, WINDOW_WIDTH, 100))
        
        # Slider
        pygame.draw.rect(screen, (100, 100, 100), slider_rect, border_radius=5)
        
        ratio = (sim.refractive_index - 1.0) / 2.0
        knob_x = slider_rect.x + int(ratio * slider_rect.width)
        pygame.draw.circle(screen, (255, 255, 255), (knob_x, slider_rect.centery), 12)
        
        # Labels
        lbl_n = font.render(f"Brytningsindex (n): {sim.refractive_index:.2f}", True, (255, 255, 255))
        screen.blit(lbl_n, (WINDOW_WIDTH//2 - lbl_n.get_width()//2, slider_rect.y - 30))
        
        screen.blit(font.render("1.0 (Luft)", True, (150,150,150)), (slider_rect.x, slider_rect.bottom + 5))
        screen.blit(font.render("3.0 (Segt)", True, (150,150,150)), (slider_rect.right - 60, slider_rect.bottom + 5))
        
        # Info
        info = font.render("Våglängden minskar och riktningen ändras för att vågtopparna ska hänga ihop!", True, (100, 200, 100))
        screen.blit(info, (WINDOW_WIDTH//2 - info.get_width()//2, 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()